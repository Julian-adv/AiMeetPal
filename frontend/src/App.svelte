<script lang="ts">
  interface Message {
    role: 'user' | 'assistant' | 'error';
    content: string;
    image?: string;
  }

  let messages: Message[] = [];
  let newMessage: string = '';
  let selectedFile: File | null = null;

  async function sendMessage(): Promise<void> {
    if (!newMessage.trim()) return;

    // 사용자 메시지 추가
    messages = [...messages, { role: 'user', content: newMessage }];
    const messageToSend = newMessage;
    newMessage = '';

    try {
      const response = await fetch('http://localhost:5000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: messageToSend }),
      });

      const data = await response.json();

      // AI 응답 추가
      messages = [...messages, { role: 'assistant', content: data.response }];
    } catch (error) {
      console.error('Error:', error);
      messages = [...messages, { role: 'error', content: '오류가 발생했습니다.' }];
    }
  }

  async function handleFileUpload(event: Event): Promise<void> {
    const target = event.target;
    if (!(target instanceof HTMLInputElement)) return;
    const file = target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:5000/api/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      if (response.ok) {
        messages = [
          ...messages,
          {
            role: 'user',
            content: '이미지 업로드: ' + file.name,
            image: URL.createObjectURL(file),
          },
        ];
      }
    } catch (error) {
      console.error('Error:', error);
    }
  }
</script>

<main>
  <div class="chat-container">
    <div class="messages">
      {#each messages as message}
        <div class="message {message.role}">
          {#if message.image}
            <img src={message.image} alt="Uploaded" />
          {/if}
          <p>{message.content}</p>
        </div>
      {/each}
    </div>

    <div class="input-container">
      <input type="file" accept="image/*" on:change={handleFileUpload} />
      <input
        type="text"
        bind:value={newMessage}
        placeholder="메시지를 입력하세요..."
        on:keydown={(e) => e.key === 'Enter' && sendMessage()}
      />
      <button on:click={sendMessage}>전송</button>
    </div>
  </div>
</main>

<style>
  .chat-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    height: 100vh;
    display: flex;
    flex-direction: column;
  }

  .messages {
    flex-grow: 1;
    overflow-y: auto;
    margin-bottom: 20px;
    padding: 10px;
    background: #f5f5f5;
    border-radius: 8px;
  }

  .message {
    margin: 10px 0;
    padding: 10px;
    border-radius: 8px;
  }

  .message.user {
    background: #e3f2fd;
    margin-left: 20%;
  }

  .message.assistant {
    background: #f5f5f5;
    margin-right: 20%;
  }

  .message.error {
    background: #ffebee;
    color: #c62828;
  }

  .message img {
    max-width: 200px;
    border-radius: 4px;
    margin-bottom: 10px;
  }

  .input-container {
    display: flex;
    gap: 10px;
    padding: 10px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  input[type='text'] {
    flex-grow: 1;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
  }

  button {
    padding: 10px 20px;
    background: #2196f3;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  button:hover {
    background: #1976d2;
  }
</style>
