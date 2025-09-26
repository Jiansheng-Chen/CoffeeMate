<template>
  
  <div class="common-layout" style="width: 100%; height:100%;">
    <el-container style="display:flex; flex-direction:column; justify-content: flex-start; width: 100%; height: 100%;">
      <el-header style="display:flex; flex:0 0 30px; overflow-y:hidden; justify-content: center; align-items: top;">
        <span>
          {{ dialogue_title }}
        </span>
      </el-header>
      <el-main class="chat-container" style="display:flex; flex-direction: column; flex:1 0 0; width: 100%; overflow-y:auto; justify-content: flex-start; align-items: center;">
        <div :class="['message-item', 'system-message']">
          <div class="avater">
            <el-icon><Coffee /></el-icon>
          </div>
          <div class="message-content">
            请问有什么可以帮到您的吗？
          </div>
        </div>
        
        <div v-for="(message, index) in dialogue_history" :key="index" :class="['message-item', message.role === 'user' ? 'user-message' : 'system-message']">
          <div class="avater" v-if="message.role === 'assistant'">
            <el-icon><Coffee /></el-icon>
          </div>
          <div class="message-content" v-if = "message.role != 'system'">
            {{ message.content }}
          </div>
          <div class="avater" v-if="message.role === 'user'">
            <el-icon><User /></el-icon>
          </div>
        </div>
        <div :class="['message-item', 'system-message']">
          <div class="avater" v-if="currentResponse != ''">
            <el-icon><Coffee /></el-icon>
          </div>
          <div class="message-content" v-if="currentResponse != ''">
            {{ currentResponse }}
          </div>
        </div>
      </el-main>
      <el-footer style="display:flex; flex:0 0 100px; overflow-y:hidden; justify-content: center; align-items: center;">
          <el-form label-width="auto" style="margin: 16px; width:100%; max-width: 800px; background-color:aliceblue; padding: 8px; padding-bottom: 20px; position: relative; border-radius: 8px;">
              <el-form-item>
                <el-input type="textarea" :row="1" v-model="query" placeholder="请在此输入内容...">
                </el-input>
              </el-form-item>
              <div class="chat_button">
                <el-form-item style="margin-bottom : 0px">
                  <el-button :icon = "Promotion" @click="sendMessageStream(query)"/>
                </el-form-item>
              </div>
          </el-form>
      </el-footer>
    </el-container>
  </div>



</template>

<script setup lang="ts">
import {onMounted, ref, nextTick} from 'vue'
import axios from 'axios';
import {Promotion, User, Coffee} from '@element-plus/icons-vue'
import { useAuthStore } from '@/sotres/auth';
import { useDialog } from 'element-plus';
import { useDialoguesStore } from '@/sotres/dialogues';
import { storeToRefs } from 'pinia';
import apiClient from '@/client';
import { onBeforeRouteUpdate } from 'vue-router';
const props = defineProps<{
  id: string | number
}>()
const dialogue_id = ref(props.id)
console.log('dialogue_id in DialogueView:',props.id)
const dialogue_title=ref("未命名")
const query =  ref('')
const dialogue_history = ref([])
const isLoading = ref(false)
const currentResponse = ref('')
const authStore = useAuthStore()
const dialoguesStore = useDialoguesStore()
const {dialogues} = storeToRefs(dialoguesStore)




const sendMessageStream = async (message) => {
            isLoading.value = true
            currentResponse.value = ''
            try {

                dialogue_history.value.push({
                  "role" : "user",
                  "content" : message,
                  "isPending" : true
                })
                query.value=''
                currentResponse.value="思考中..."

                const response = await fetch('http://localhost:8000/dialogue/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization' : `Bearer ${authStore.token}`
                    },
                    body: JSON.stringify({
                        dialogue_id: dialogue_id.value,
                        query: message,
                        history: dialogue_history.value
                    })
                })
                
                

                const reader = response.body.getReader()
                const decoder = new TextDecoder()
                
                let accumulatedData = ''
                
                while (true) {
                    const { done, value } = await reader.read()
                    if (done) break
                    
                    const chunk = decoder.decode(value)
                    accumulatedData += chunk
                    
                    // 处理 SSE 格式的数据
                    let lines = accumulatedData.split('\n\n')
                    accumulatedData = lines.pop() // 保留不完整的行
                    
                    for (let line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.slice(6))
                                handleStreamData(data)
                            } catch (e) {
                                console.error('解析流数据错误:', e)
                            }
                        }
                    }
                }
                
            } catch (error) {
                console.error('流式请求错误:', error)
            } finally {
                isLoading.value = false
            }
        }
        

 const handleStreamData = (data) => {
            switch (data.type) {
                case 'start':
                    dialogue_id.value = data.dialogue_id
                    console.log('开始接收响应:', data)
                    break
                    
                case 'chunk':
                    // 实时显示响应内容
                    currentResponse.value += data.content
          
                    scrollToBottom()
                    break
                    
                case 'end':
                    // 响应结束，更新完整历史
                    const userMessage = {
                        role: 'user',
                        content: dialogue_history.value.find(m => m.isPending && m.role === 'user')?.content
                    }
                    const assistantMessage = {
                        role: 'assistant',
                        content: data.final_response
                    }
                    const newMessages = [userMessage, assistantMessage]
                    dialogue_history.value = dialogue_history.value.filter(m => !m.isPending)
                    console.log("filter history:", dialogue_history.value)
                    dialogue_history.value.push(...newMessages)
                    currentResponse.value = ''
                    console.log("newMessage:",newMessages)
                    dialoguesStore.appendHistoryById(newMessages,dialogue_id.value)

                    break
                    
                case 'error':
                    console.error('服务器错误:', data.message)
                    break
            }
        }
        
        const scrollToBottom = () => {
            // 实现滚动到底部的逻辑
            nextTick(() => {
                const container = document.querySelector('.chat-container')
                if (container) {
                    container.scrollTop = container.scrollHeight
                }
            })
        }

const load_dialogues = async (id) => {
    try{
      const dialogue = dialoguesStore.findDialogueById(id)
      console.log('避免重新加载1', dialogue)
      if (dialogue != null){//避免重复加载
        console.log('避免重新加载', dialogue)
        dialogue_history.value = dialogue.history
        dialogue_title.value = dialogue.title
      }
      else{
        console.log("从数据库get_history_by_id")
        const response = await apiClient.post('/dialogue/get_history_by_id',{dialogue_id:id})
        dialogue_history.value = response.data.history
        dialogue_title.value = response.data.title
        console.log("从数据库get_history_by_id后，得到的来自服务器的回答：",response.data)
        dialoguesStore.addDialogue(response.data)
      }
    console.log('请求成功')
  }catch(error){
    console.error('请求失败：',error)
  }
}

onMounted(async () => {
  console.log("dialogueview onmounted")
  load_dialogues(dialogue_id.value)
})

onBeforeRouteUpdate((to) => {
  console.log("onBeforeRouteUpdate", to)
  load_dialogues(to.params.id)
  currentResponse.value =''
  dialogue_id.value = to.params.id as string
})

//onMouted加载id对应dialogue，然后把dialogue的内容整成ref 再整el-container布局输出
</script>

<style scoped>
.common-layout {
  height: 100%;
  width: 100%;
}

.chat_input {
  position: relative;
  width: 100%;
  height: 100%;
  background-color: antiquewhite;
  border-radius: 8px;
}

.chat_button{
  position: absolute;
  bottom: 4px;
  right: 8px;
}

.message-item {
  display: flex;
  width: 80%;
  flex: 0 0 auto;
}

.system-message{
  justify-content: flex-start;
}

.user-message{
  justify-content: flex-end;
}

.avater{
  width: 40px;
  height: 40px;
  display: flex;
  justify-content: center;
  align-items: top;
}

.message-content {
  border: 1px;
  padding: 12px 16px;
  border-radius: 18px;
  word-wrap: break-word;    /* 长文本换行 */
  line-height: 1.4;
  min-width: 0;             /* 允许文本换行 */
  max-width: 300px;
}

.system-message .message-content {
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.user-message .message-content {
  background-color: #1976d2;
  color: white;
  border-radius: 8px;
}
</style>

