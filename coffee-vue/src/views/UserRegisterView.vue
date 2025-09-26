
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
              <div class="welcome-title">  欢迎注册！</div>
            </el-form-item>
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="ruleForm.email" />
            </el-form-item>
            <el-form-item label="昵称" prop="name">
              <el-input v-model="ruleForm.name" />
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input v-model="ruleForm.password" type="password" autocomplete="off" />
            </el-form-item>
            <el-form-item label="确认密码" prop="checkPassword">
              <el-input
                v-model="ruleForm.checkPassword"
                type="password"
                autocomplete="off"
              />
            </el-form-item>
           
            <el-form-item class="button">
              <el-button type="primary" @click="submitForm(ruleFormRef)">
                注册
              </el-button>
              <el-button @click="resetForm(ruleFormRef)">清空内容</el-button>
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
const router = useRouter()
const ruleForm = reactive({
  email : '',
  name : '',
  password : '',
  checkPassword : '',
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

const checkName = (rule: any, value: any, callback: any) => {
  if(!value){
    return callback(new Error("请输入名字!"))
  }
  callback()
}

const validatePass = (rule: any, value: any, callback: any) => {
  if (value === '') {
    callback(new Error('Please input the password'))
  } else {
    if (ruleForm.checkPassword !== '') {
      if (!ruleFormRef.value) return
      ruleFormRef.value.validateField('checkPass')
    }
    callback()
  }
}
const validatePass2 = (rule: any, value: any, callback: any) => {
  if (value === '') {
    callback(new Error('Please input the password again'))
  } else if (value !== ruleForm.password) {
    callback(new Error("Two inputs don't match!"))
  } else {
    callback()
  }
}


const rules = reactive<FormRules<typeof ruleForm>>({
  email : [{validator: checkEmail, trigger : 'blur'}],
  name : [{validator: checkName, trigger : 'blur' }],
  password: [{ validator: validatePass, trigger : 'blur' }],
  checkPassword: [{ validator: validatePass2, trigger: 'blur' }],
})

const submitForm = (formEl: FormInstance | undefined) => {
  if (!formEl) return
  formEl.validate(async (valid) => {
    if (valid) {
      console.log('submit!')
       try {
        const formData = new FormData()
        formData.append('email', ruleForm.email)
        formData.append('name', ruleForm.name)
        formData.append('password', ruleForm.password)
        const response = await axios.post('http://localhost:8000/user/register', formData,{
          headers:{
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        })//这里要填个url
        console.log('注册成功:', response.data)
        // 处理成功逻辑
        
        // 比如显示成功消息
        ElMessage.success('注册成功！')
        
        router.push('/user/login')
        
      } catch (error: any) {
        console.error('注册失败:', error)
        
        // 显示错误消息
        if (error.response) {
          // 服务器返回错误状态码
          ElMessage.error(error.response.data.message || '注册失败')
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

const resetForm = (formEl: FormInstance | undefined) => {
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