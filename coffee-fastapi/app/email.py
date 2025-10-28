from Config import config
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import FastAPI, BackgroundTasks, HTTPException, status
import asyncio
async def send_reset_email(user_email : str, token : str):
    
    FRONTEND_RESET_URL = config.get("FRONTEND_RESET_URL")
    SMTP_HOST = config.get("SMTP_HOST")
    SMTP_PORT = config.get("SMTP_PORT")
    SMTP_USER = config.get("SMTP_USER")
    SMTP_PASSWORD = config.get("SMTP_PASSWORD")
    RESET_TOKEN_EXPIRE_MINUTES = config.get("RESET_TOKEN_EXPIRE_MINUTES")
    reset_link = f"{FRONTEND_RESET_URL}?token={token}"
    # 简单 HTML 邮件模板（也可从文件读取）
    html_content = f"""
    <p>请点击以下链接以重置密码：{reset_link}</p>
    <p>链接将在 {RESET_TOKEN_EXPIRE_MINUTES} 分钟后失效。</p>
    <p>如果您未请求此操作，请忽略此邮件。</p>
    """

    message = MIMEMultipart("alternative")
    message["Subject"] = "重置您的密码"
    message["From"] = SMTP_USER
    message["To"] = user_email

    part = MIMEText(html_content, "html")
    message.attach(part)

    try:
        await aiosmtplib.send(
            message,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            start_tls=True,
            username=SMTP_USER,
            password=SMTP_PASSWORD,
        )
    except Exception as e:
        print(f"邮件发送失败: {e}")
        raise HTTPException(status_code=500, detail="邮件发送失败")