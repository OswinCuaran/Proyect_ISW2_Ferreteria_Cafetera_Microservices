const nodemailer = require('nodemailer');

let transporter = null;
if (process.env.SMTP_HOST) {
  transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST,
    port: Number(process.env.SMTP_PORT) || 587,
    secure: Number(process.env.SMTP_PORT) === 465,
    auth: process.env.SMTP_USER
      ? { user: process.env.SMTP_USER, pass: process.env.SMTP_PASSWORD }
      : undefined,
  });
}

async function sendMail({ to, subject, text }, correlationId) {
  if (!transporter) {
    console.log(
      `[CORREO SIMULADO] correlation_id=${correlationId} para=${to.join(', ')} asunto="${subject}"\n${text}`
    );
    return;
  }
  await transporter.sendMail({
    from: process.env.SMTP_FROM || process.env.SMTP_USER,
    to: to.join(', '),
    subject,
    text,
  });
}

module.exports = { sendMail };