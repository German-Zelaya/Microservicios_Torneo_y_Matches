import amqplib from "amqplib";
import dotenv from "dotenv";

dotenv.config();

let channel = null;

export const connectRabbitMQ = async () => {
  try {
    const connection = await amqplib.connect(process.env.RABBITMQ_URL);
    channel = await connection.createChannel();
    console.log("🐇 RabbitMQ conectado");
  } catch (err) {
    console.error("❌ Error conectando RabbitMQ:", err);
  }
};

export const publishEvent = async (queue, event) => {
  if (!channel) {
    console.error("RabbitMQ no está inicializado.");
    return;
  }

  await channel.assertQueue(queue, { durable: true });
  channel.sendToQueue(queue, Buffer.from(JSON.stringify(event)), {
    persistent: true,
  });

    console.log(`📤 Evento enviado a ${queue}:`, event);
};
