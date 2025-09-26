<template>


  <div class="common-layout">
      <el-container>
        <el-aside id="el-aside" :width="isCollapse ? '64px' : '200px'">

            <!-- <el-radio-group v-model="isCollapse" class="btn-group" style="margin-bottom: 20px">
                <el-radio-button :value="false" v-show="isCollapse" >-></el-radio-button>
                <el-radio-button :value="true" v-show="!isCollapse" ><-</el-radio-button>
            </el-radio-group> -->
            
            <el-menu
              default-active="1"
              class="el-menu-vertical-demo"
              :collapse="isCollapse"
              @open="handleOpen"
              @close="handleClose"
            >
              <div class="collapse-btn" >
                <el-button type="type" @click="toggleCollapse">
                  <span v-if="isCollapse">▶</span>
                  <span v-else>◀</span>
                </el-button>
              </div>
              
              
                
              
              <el-menu-item index="1" @click="new_dialogue" class="menu-top">
                <el-icon><ChatDotRound /></el-icon>
                <span>新建对话</span>
              </el-menu-item>
              
              

              <el-sub-menu index="2">
                <template #title>
                  <el-icon><document /></el-icon>
                  <span>历史对话</span>
                </template>
                <el-menu-item v-for="(item, index) in dialogues" 
                :key="item.id || index" 
                :index="'2-'+(index+1)" 
                @click="show_dialogue(item.id)">
                  {{item.title}}
                </el-menu-item>
              </el-sub-menu>

              <el-sub-menu index="3" class="menu-bottom">
                
                <template #title>
                  <el-icon><User /></el-icon>
                  <span>用户</span>
                </template>
                <RouterLink :to="`/user/login`" custom v-slot="{href, navigate}">
                  <el-menu-item index="3-1" @click="navigate">用户登录</el-menu-item>
                </RouterLink>
                <RouterLink :to="`/user/register`" custom v-slot="{href, navigate}">
                  <el-menu-item index="3-2" @click="navigate">用户注册</el-menu-item>
                </RouterLink>
                <RouterLink :to="`/user/info/${user_id}`" custom v-slot="{href, navigate}">
                  <el-menu-item index="3-3" @click="navigate">用户信息</el-menu-item>
                </RouterLink>
                
              </el-sub-menu>
            </el-menu>
        </el-aside>
      <el-main>
        <RouterView />
      </el-main>
      
    </el-container>
  </div>

  
  
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import {useRouter, useRoute} from 'vue-router'
import {
  Document,
  Menu as IconMenu,
  User,
  ChatDotRound,
} from '@element-plus/icons-vue'
import { useDialoguesStore } from '@/sotres/dialogues'
import { useAuthStore } from '@/sotres/auth'
import { storeToRefs } from 'pinia'
import apiClient from '@/client'

const dialoguesStore = useDialoguesStore()
const {dialogues} =storeToRefs(dialoguesStore)

const authStore = useAuthStore()

const router = useRouter()
const route = useRoute()
const user_id=ref('')

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}
const isCollapse = ref(true)
const handleOpen = (key: string, keyPath: string[]) => {
  console.log(key, keyPath)
}
const handleClose = (key: string, keyPath: string[]) => {
  console.log(key, keyPath)
}

// onMounted(async () => {
//   // if(!authStore.token){
//   //   router.push('/user/login')
//   // }
// })

const new_dialogue = async () => {
  try{
    
    
    const new_dialogue = await apiClient.post(`/dialogue/get_new_dialogue`)
    dialoguesStore.addDialogue(new_dialogue.data)
    router.push(`/dialogue/${new_dialogue.data.id}`)
    
  } catch (error) {
    console.error('请求失败:', error)
  }
}

const show_dialogue = async ( dialogue_id : string | number) => {
  router.push(`/dialogue/${dialogue_id}`)
}

</script>

<style scoped>

:deep(.el-container){
  width: 100vw;
  height: 100vh;
}

:deep(.el-aside) {
  position: relative;
  height: 100vh;
  display: flex;
  flex-direction: column;
}


:deep(.el-aside > .el-menu-vertical-demo) {
  width: 64px;
  height: 100%;
  position: relative;
  padding-top: 64px; 
  padding-bottom: 64px; 
  overflow-y: auto;
}

:deep(.el-menu-vertical-demo):not(.el-menu--collapse) {
  width: 200px;
  height: 100%;
  position: relative;
  padding-top: 64px; 
  padding-bottom: 64px; 
  overflow-y: auto;
}

.collapse-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 10;
  height: 64px;
}

.menu-bottom {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
}

:deep(.el-container .el-main){
  display: flex;
  
}
</style>