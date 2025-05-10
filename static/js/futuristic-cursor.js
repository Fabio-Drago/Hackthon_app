// Arquivo: static/js/futuristic-cursor.js

// Verificar se está em desktop
if (window.innerWidth >= 1024) {
  document.addEventListener('DOMContentLoaded', function() {
    // Criar elementos do cursor
    const cursorDot = document.createElement('div');
    cursorDot.classList.add('cursor-dot');
    document.body.appendChild(cursorDot);

    const cursorOutline = document.createElement('div');
    cursorOutline.classList.add('cursor-outline');
    document.body.appendChild(cursorOutline);

    // Rastrear movimento do mouse
    document.addEventListener('mousemove', function(e) {
      // Atualizar posição do cursor principal com atraso mínimo
      cursorDot.style.left = e.clientX + 'px';
      cursorDot.style.top = e.clientY + 'px';
      
      // Atualizar posição do círculo externo com um pequeno atraso para efeito de suavidade
      setTimeout(() => {
        cursorOutline.style.left = e.clientX + 'px';
        cursorOutline.style.top = e.clientY + 'px';
      }, 50);
      
      // Adicionar efeito de rastro a cada X movimentos
      if (Math.random() > 0.92) {
        createTrail(e.clientX, e.clientY);
      }
    });

    // Detectar clique
    document.addEventListener('mousedown', function() {
      cursorDot.classList.add('cursor-click');
      cursorOutline.classList.add('cursor-click');
      setTimeout(() => {
        cursorDot.classList.remove('cursor-click');
        cursorOutline.classList.remove('cursor-click');
      }, 300);
    });

    // Adicionar efeito hover para elementos clicáveis
    const clickableElements = document.querySelectorAll('a, button, input, select, textarea, [role="button"]');
    clickableElements.forEach(element => {
      element.addEventListener('mouseover', function() {
        cursorDot.classList.add('cursor-hover');
        cursorOutline.classList.add('cursor-hover');
      });
      
      element.addEventListener('mouseout', function() {
        cursorDot.classList.remove('cursor-hover');
        cursorOutline.classList.remove('cursor-hover');
      });
    });

    // Ocultar o cursor ao sair da janela
    document.addEventListener('mouseout', function(e) {
      if (e.relatedTarget === null) {
        cursorDot.style.opacity = '0';
        cursorOutline.style.opacity = '0';
      }
    });

    // Mostrar o cursor ao entrar na janela
    document.addEventListener('mouseover', function() {
      cursorDot.style.opacity = '1';
      cursorOutline.style.opacity = '1';
    });

    // Função para criar efeito de rastro
    function createTrail(x, y) {
      const trail = document.createElement('div');
      trail.classList.add('cursor-trail');
      trail.style.left = x + 'px';
      trail.style.top = y + 'px';
      document.body.appendChild(trail);
      
      // Remover o elemento do rastro após a animação
      setTimeout(() => {
        document.body.removeChild(trail);
      }, 1000);
    }

    // Efeito 3D de rotação do cursor baseado na posição do mouse
    document.addEventListener('mousemove', function(e) {
      // Calcular a rotação com base na posição do mouse relativa ao centro da janela
      const centerX = window.innerWidth / 2;
      const centerY = window.innerHeight / 2;
      
      const angleX = (e.clientY - centerY) / centerY * 10; // Ajuste o multiplicador para mais ou menos inclinação
      const angleY = (e.clientX - centerX) / centerX * -10; // Sinal negativo para rotação correta
      
      cursorOutline.style.transform = `translate(-50%, -50%) rotateX(${angleX}deg) rotateY(${angleY}deg)`;
    });
    
    // Atualizar cursores quando novos elementos são adicionados ao DOM (por exemplo, após carregamento AJAX)
    const observer = new MutationObserver(function(mutations) {
      mutations.forEach(function(mutation) {
        if (mutation.addedNodes.length) {
          const newClickableElements = document.querySelectorAll('a, button, input, select, textarea, [role="button"]');
          newClickableElements.forEach(element => {
            if (!element.hasMouseListeners) {
              element.addEventListener('mouseover', function() {
                cursorDot.classList.add('cursor-hover');
                cursorOutline.classList.add('cursor-hover');
              });
              
              element.addEventListener('mouseout', function() {
                cursorDot.classList.remove('cursor-hover');
                cursorOutline.classList.remove('cursor-hover');
              });
              
              element.hasMouseListeners = true;
            }
          });
        }
      });
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
  });
}