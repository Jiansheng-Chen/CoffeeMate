



<template>

  <div class="common-layout">
    <el-container>
      <el-header>
        <img src="@/assets/logo.png" alt="Logo" style="height: 50px; width: 50px;" />
        
      </el-header>
      <el-main>
        <div class="login-form">
          <el-form
      ref="ruleFormRef"
      :model="ruleForm"
      status-icon = True
      :rules="rules"
      label-width="auto"
      class="demo-ruleForm"
          >
            <el-form-item>
              <div class="welcome-title"> 欢迎登录！</div>
            </el-form-item>
            <el-form-item label="邮箱" prop="username">
              <el-input v-model="ruleForm.username" />
            </el-form-item>
            
            <el-form-item label="密码" prop="password">
              <el-input v-model="ruleForm.password" type="password" autocomplete="off" />
            </el-form-item>
            <el-form-item class="button">
              <el-button type="primary" @click="submitForm(ruleFormRef)">
                登录
              </el-button>
              <el-button @click="resetPass(ruleFormRef)">忘记密码？</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-main>
      <el-footer>
        <div style="display: flex; justify-content: space-between; align-items: flex-end; width: 100%;">
          <div>
            <img src="@/assets/logo.png" alt="Logo" style="height: 20px; width: 20px; margin: 5px;" />
          </div>
          
          <div>
            <a href="https://github.com/Jiansheng-Chen?tab=repositories" target="_blank" rel="noopener noreferrer" style="display: inline-block;">
              <img src="@/assets/github.png" alt="Github" style="height: 20px; width: 20px; margin: 5px; " />
            </a>
            <a href="https://xhslink.com/m/7ppJuWmmXXV?xhsshare=CopyLink&appuid=5f62ee700000000001002f03&apptime=1757401226&share_id=85161e94a308404393771a840d26109e&share_channel=copy_link" target="_blank" rel="noopener noreferrer" style="display: inline-block;">
              <img src="@/assets/xhslogo.png" alt="XHS" style="height: 20px; width: 20px; margin: 5px;" />
            </a>
            
          </div>
          
        </div>
        <el-divider style="margin: 5px 0;" />
        <div style="display: flex; justify-content: space-between; align-items: flex-end; width: 100%;">
          <el-text class="mx-1" type="info">FreewillCoffee</el-text>
          <el-text class="mx-1" type="info">店铺地址：肇庆市端州区建设三路肇庆市跃龙路78号首层</el-text>
        </div>
      </el-footer>
    </el-container>
  </div>


  
</template>



<script lang="ts" setup>
import { reactive, ref } from 'vue'
import {useRouter} from 'vue-router'
import axios from 'axios'
import {ElMessage} from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '@/sotres/auth'
import { useDialoguesStore } from '@/sotres/dialogues'
//import { URLSearchParams } from 'url'
import { storeToRefs } from 'pinia'
import apiClient from '@/client'
const authStore = useAuthStore()
const dialoguesStore = useDialoguesStore()
//const dialogues = dialoguesStore.dialogues
const {dialogues} = storeToRefs(dialoguesStore)
const router = useRouter()
const ruleForm = reactive({
  username : '',
  password : '',
})
const ruleFormRef = ref<FormInstance>()

const checkEmail = (rule: any, value: any, callback: any) => {
  if (!value) {
    return callback(new Error('请输入邮箱！'))
  }
  const emailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/
  
  if (!emailRegex.test(value)) {
    return callback(new Error('请输入正确的邮箱！'))
  }
  
  // 验证通过
  callback()
}


const validatePass = (rule: any, value: any, callback: any) => {
  if (value === '') {
    callback(new Error('Please input the password'))
  } 
  callback()
}



const rules = reactive<FormRules<typeof ruleForm>>({
  username : [{validator: checkEmail, trigger : 'blur'}],
  password: [{ validator: validatePass, trigger : 'blur' }],
})

const submitForm = (formEl: FormInstance | undefined) => {
  if (!formEl) return
  formEl.validate(async (valid) => {
    if (valid) {
      console.log('submit!')
       try {
        const params = new URLSearchParams()
        
        params.append('username', ruleForm.username)
        params.append('password', ruleForm.password)
        params.append('grant_type', 'password')

        
        const response = await axios.post(
          'http://localhost:8000/user/login',
          params, 
          {
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded'
            }
          }
        )
        
        console.log('登录成功:', response.data)
        // 处理成功逻辑
        
        // 比如显示成功消息
        
        ElMessage.success('登录成功！')


        
        
        authStore.setToken(response.data.access_token)
        authStore.setIsLogged(true)
        
        dialoguesStore.clear()
        const response_dialogue = await apiClient.post('/dialogue/get_ids_titles')
        dialoguesStore.setDialogue(response_dialogue.data)
        
        
        
        
        console.log("dialoguesStore in UserLoginView:", dialoguesStore.getDialogue())

        
        try{
        dialogues.value.forEach(d => {
        console.log(`标题: ${d.title}, ID: ${d.id}`)
          })
        } catch (error) {
          console.error('加载对话失败:', error)
        }
        //console.log(`response_dialogue in login : ${dialoguesStore.getDialogue()}`)

        const to_dialogue_id = response_dialogue.data?.[0]?.id
        if(to_dialogue_id){
          router.push(`/dialogue/${to_dialogue_id}`)
        }
        else{
          const new_dialogue = await apiClient.post(`/dialogue/get_new_dialogue`)
          dialoguesStore.addDialogue(new_dialogue.data)
          console.log(`new_dialogue in UserLogin: ${new_dialogue.data}`)
          router.push(`/dialogue/${new_dialogue.data.id}`)
        }
        

        console.log(authStore.token)
      } catch (error: any) {
        console.error('登录失败:', error)
        
        // 显示错误消息
        if (error.response) {
          // 服务器返回错误状态码
          ElMessage.error(error.response.data.message || '登录失败')
        } else {
          // 网络错误
          ElMessage.error('网络连接失败')
        }
      }
    } else {
      console.log('error submit!')
    }
  })
}

const resetPass = (formEl: FormInstance | undefined) => {
  if (!formEl) return
  formEl.resetFields()
}
</script>


<style scoped>


.common-layout{
  height: 100%;
  width: 100%;
}

.common-layout > :deep(.el-container){
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
}

.common-layout > :deep(.el-container > .el-header){
  display: flex;
  flex: 0 1 50px;
  width: 100%;
  justify-content: flex-start;
  align-items: center;
}

.common-layout > :deep(.el-container > .el-main){
  display: flex;
  flex: 1 1 0;
  justify-content: center;
  align-items: center;  
  width: 100%;
}

.common-layout > :deep(.el-container > .el-footer){
  display: flex;
  flex-direction: column;
  flex: 0 1 80px;
  justify-content: flex-end;
  align-items: flex-start;
  width: 100%;
}

.login-form{
  border-radius: 40px;
  box-shadow: 5px 5px 10px rgba(0, 0, 0, 0.3);
  height: 400px;
  width: 500px;
}

.login-form > :deep(.el-form){
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  justify-content: center;
  align-items: center;
}


.login-form > :deep(.el-form > .el-form-item):not(.button) {
  flex: 1 1 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 5px;
  width: 80%;
}

.button{
  flex: 1 1 0;
  display: flex;
  align-items: center;
  justify-content:flex-end;
  padding: 5px;
  width: 80%;
  
}

.button > :deep(.el-form-item__content){
  flex: 1 1 0;
  display: flex;
  align-items: center;
  justify-content:flex-end;
  padding: 5px;
  width: 100%;
  
}

.welcome-title {
  font-size: 36px;
  font-weight: bold;
  text-align: center;
  color: #409eff; /* Element Plus 主题色 */
  width: 80%;
  letter-spacing: 2px;
  margin-top: 10px;
  flex: 1 0 60px;
  justify-self: center;
  margin-left: 50px;
}

</style>