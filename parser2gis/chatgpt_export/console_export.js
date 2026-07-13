// ChatGPT Conversation Exporter
// Paste this into the browser console on https://chatgpt.com/c/...
// It extracts all messages and copies markdown to your clipboard.

(function () {
  'use strict';

  function extractConversation() {
    const articles = document.querySelectorAll('article[data-testid^="conversation-turn-"]');
    if (!articles.length) {
      console.error('No conversation turns found. Make sure you are on a ChatGPT conversation page.');
      return null;
    }

    const messages = [];
    articles.forEach((article) => {
      const turnAttr = article.getAttribute('data-testid') || '';
      const turnMatch = turnAttr.match(/conversation-turn-(\d+)/);
      const turnNumber = turnMatch ? parseInt(turnMatch[1], 10) : messages.length + 1;

      let role = 'unknown';
      if (article.querySelector('[data-message-author-role="user"]')) {
        role = 'user';
      } else if (article.querySelector('[data-message-author-role="assistant"]')) {
        role = 'assistant';
      } else if (article.querySelector('[data-message-author-role="tool"]')) {
        role = 'tool';
      }

      const contentDiv = article.querySelector('[data-message-author-role]') || article;
      const textParts = [];
      const codeBlocks = contentDiv.querySelectorAll('pre code');
      const codeContents = [];
      codeBlocks.forEach((block) => {
        codeContents.push(block.textContent);
      });

      function extractText(node) {
        if (node.nodeType === Node.TEXT_NODE) {
          return node.textContent;
        }
        if (node.nodeType === Node.ELEMENT_NODE) {
          if (node.tagName === 'CODE' && node.closest('pre')) {
            return null;
          }
          if (node.tagName === 'PRE') {
            const lang = node.querySelector('code')?.className?.replace(/^language-/, '') || '';
            const code = node.textContent;
            return '```' + (lang || '') + '\n' + code.trim() + '\n```';
          }
          let result = '';
          node.childNodes.forEach((child) => {
            const text = extractText(child);
            if (text !== null) {
              result += text;
            }
          });
          if (node.tagName === 'P') result += '\n\n';
          if (node.tagName === 'LI') result = '• ' + result.trim() + '\n';
          if (node.tagName === 'BR') result += '\n';
          if (['H1', 'H2', 'H3', 'H4'].includes(node.tagName)) {
            const level = parseInt(node.tagName[1], 10);
            result = '#'.repeat(level) + ' ' + result.trim() + '\n\n';
          }
          return result;
        }
        return '';
      }

      extractText(contentDiv);
      // Simpler approach: get all text content with structure
      const walker = document.createTreeWalker(contentDiv, NodeFilter.SHOW_ALL, null, false);
      let structured = '';
      let inCode = false;
      while (walker.nextNode()) {
        const node = walker.currentNode;
        if (node.tagName === 'PRE') {
          const code = node.querySelector('code');
          const lang = code?.className?.replace(/^language-/, '') || '';
          structured += '```' + (lang || '') + '\n' + (code?.textContent || node.textContent).trim() + '\n```\n\n';
          walker.nextNode();
          continue;
        }
        if (node.tagName === 'CODE') continue;
        if (node.nodeType === Node.TEXT_NODE && node.textContent.trim()) {
          structured += node.textContent;
        }
        if (node.tagName === 'P') structured += '\n\n';
        if (node.tagName === 'BR') structured += '\n';
        if (node.tagName === 'LI') structured = structured.trimEnd() + '\n';
      }
      structured = structured.trim();

      messages.push({
        turn: turnNumber,
        role: role,
        content: structured,
      });
    });

    return messages;
  }

  function toMarkdown(messages) {
    const lines = ['# ChatGPT Conversation Export', '', '---', ''];
    messages.forEach((msg, i) => {
      const label = { user: 'User', assistant: 'Assistant', tool: 'Tool' }[msg.role] || msg.role;
      lines.push('### ' + label, '');
      if (msg.content) {
        lines.push(msg.content);
      } else {
        lines.push('*[empty message]*');
      }
      lines.push('');
      if (i < messages.length - 1) lines.push('---', '');
    });
    return lines.join('\n');
  }

  const messages = extractConversation();
  if (!messages) return;

  console.log(`Found ${messages.length} messages`);
  messages.forEach((m) => console.log(`  ${m.turn}. [${m.role}] ${m.content.slice(0, 80)}...`));

  const md = toMarkdown(messages);
  try {
    navigator.clipboard.writeText(md).then(() => {
      console.log('Markdown copied to clipboard!');
    }).catch(() => {
      console.log('Clipboard write failed. Here is the markdown:');
      console.log(md);
    });
  } catch (e) {
    console.log('Clipboard API not available. Here is the markdown:');
    console.log(md);
  }

  console.log('--- Full markdown below ---');
  console.log(md);
  console.log('--- End ---');
})();
