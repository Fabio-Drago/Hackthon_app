// Arquivo: static/js/landing-particles.js

// Configuração e inicialização das partículas
// Mantido o código de inicialização de partículas fornecido pelo usuário
function initParticles() {
    if (typeof particlesJS !== 'undefined') {
      particlesJS('particles-js', {
        "particles": {
          "number": {
            "value": 80,
            "density": {
              "enable": true,
              "value_area": 800
            }
          },
          "color": {
            "value": "#ffffff" // Cor das partículas (usando a cor do código fornecido)
          },
          "shape": {
            "type": "circle",
            "stroke": {
              "width": 0,
              "color": "#000000"
            },
            "polygon": {
              "nb_sides": 5
            }
            // Removido a imagem de github.svg, mantendo apenas o círculo
            // "image": {
            //     "src": "img/github.svg",
            //     "width": 100,
            //     "height": 100
            // }
          },
          "opacity": {
            "value": 0.3, // Opacidade (usando o valor do código fornecido)
            "random": true, // Random (usando o valor do código fornecido)
            "anim": {
              "enable": true, // Animação de opacidade (usando o valor do código fornecido)
              "speed": 1,
              "opacity_min": 0.1,
              "sync": false
            }
          },
          "size": {
            "value": 3,
            "random": true,
            "anim": {
              "enable": false,
              "speed": 40,
              "size_min": 0.1,
              "sync": false
            }
          },
          "line_linked": {
            "enable": true,
            "distance": 150,
            "color": "#ffffff", // Cor das linhas (usando a cor do código fornecido)
            "opacity": 0.2, // Opacidade das linhas (usando o valor do código fornecido)
            "width": 1
          },
          "move": {
            "enable": true,
            "speed": 2, // Velocidade (usando o valor do código fornecido)
            "direction": "none",
            "random": false,
            "straight": false,
            "out_mode": "out",
            "bounce": false,
            "attract": {
              "enable": false,
              "rotateX": 600,
              "rotateY": 1200
            }
          }
        },
        "interactivity": {
          "detect_on": "canvas",
          "events": {
            "onhover": {
              "enable": true,
              "mode": "grab" // Modo hover (usando o valor do código fornecido)
            },
            "onclick": {
              "enable": true,
              "mode": "push"
            },
            "resize": true
          },
          "modes": {
            "grab": {
              "distance": 140, // Distância do grab (usando o valor do código fornecido)
              "line_linked": {
                "opacity": 0.5 // Opacidade da linha no grab (usando o valor do código fornecido)
              }
            },
            "bubble": {
              "distance": 400,
              "size": 40,
              "duration": 2,
              "opacity": 8,
              "speed": 3
            },
            "repulse": {
              "distance": 200,
              "duration": 0.4
            },
            "push": {
              "particles_nb": 4
            },
            "remove": {
              "particles_nb": 2
            }
          }
        },
        "retina_detect": true
      });
    }
  }

// --- Código para o Contador Regressivo ---

// Define a data e hora alvo para o contador regressivo
// Formato: "Mês Dia, Ano Hora:Minuto:Segundo"
// Exemplo: "May 20, 2025 10:00:00" (20 de Maio de 2025 às 10:00:00)
const targetDate = new Date("May 20, 2025 10:00:00").getTime(); // <-- Lembre-se de mudar esta data!

// Seleciona os elementos onde o tempo será exibido
const daysSpan = document.getElementById('days');
const hoursSpan = document.getElementById('hours');
const minutesSpan = document.getElementById('minutes');
const secondsSpan = document.getElementById('seconds');

// Função para atualizar o contador
function updateCountdown() {
    // Verifica se todos os elementos foram encontrados antes de tentar atualizar
    if (!daysSpan || !hoursSpan || !minutesSpan || !secondsSpan) {
        // console.error("Elementos do contador regressivo não encontrados!"); // Removido para evitar spam no console em outras páginas
        return; // Sai da função se os elementos não existirem (útil em páginas que não têm o contador)
    }

    // Obtém a data e hora atuais
    const now = new Date().getTime();

    // Calcula a diferença de tempo entre a data alvo e a data atual
    const distance = targetDate - now;

    // Se a contagem regressiva terminou...
    if (distance < 0) {
        clearInterval(countdownInterval); // Para o intervalo
        daysSpan.innerHTML = "00";
        hoursSpan.innerHTML = "00";
        minutesSpan.innerHTML = "00";
        secondsSpan.innerHTML = "00";
        // Você pode adicionar uma mensagem ou ação aqui quando a contagem terminar
        console.log("Hackathon começou!");
        return; // Sai da função
    }

    // Calcula dias, horas, minutos e segundos restantes
    const days = Math.floor(distance / (1000 * 60 * 60 * 24));
    const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((distance % (1000 * 60)) / 1000);

    // Atualiza o HTML com os novos valores (adiciona zero à esquerda se necessário)
    daysSpan.innerHTML = String(days).padStart(2, '0');
    hoursSpan.innerHTML = String(hours).padStart(2, '0');
    minutesSpan.innerHTML = String(minutes).padStart(2, '0');
    secondsSpan.innerHTML = String(seconds).padStart(2, '0');
}

// --- Inicialização quando a página estiver carregada ---

document.addEventListener('DOMContentLoaded', function() {
    // Iniciar o contador apenas se os elementos existirem na página
    if (document.getElementById('days')) {
        updateCountdown(); // Chama uma vez imediatamente
        const countdownInterval = setInterval(updateCountdown, 1000); // Atualiza a cada segundo
    }

    // Tentar inicializar as partículas
    // Adicionado uma verificação para particlesJS para evitar erros em páginas sem o canvas
    if (typeof particlesJS !== 'undefined' && document.getElementById('particles-js')) {
         setTimeout(initParticles, 100); // Pequeno delay para garantir que o DOM está pronto
    }


    if (menuToggle && navigation) {
        menuToggle.addEventListener('click', function() {
            navigation.classList.toggle('active');
            menuToggle.classList.toggle('active'); // Opcional: Adicionar classe ao botão para animar o hamburger
        });

        // Opcional: Fechar o menu ao clicar em um link
        // navigation.querySelectorAll('a').forEach(link => {
        //     link.addEventListener('click', function() {
        //         navigation.classList.remove('active');
        //         menuToggle.classList.remove('active');
        //     });
        // });
    }
});

// Tentar novamente inicializar as partículas quando a janela terminar de carregar
// Adicionado uma verificação para particlesJS e o elemento canvas
window.addEventListener('load', function() {
     if (typeof particlesJS !== 'undefined' && document.getElementById('particles-js')) {
        initParticles();
     }
});

// --- Script para o formulário da newsletter (Adicionado) ---
    // O envio do formulário será tratado pelo Flask no backend na rota '/subscribe'.
    // O JavaScript aqui é apenas para referência ou para adicionar validações front-end no futuro.
    const newsletterForm = document.getElementById('newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(event) {
            // Para validação front-end, você pode adicionar código aqui:
            // const emailInput = newsletterForm.querySelector('.newsletter-input');
            // if (!emailInput.value.includes('@')) {
            //     alert('Por favor, insira um email válido.');
            //     event.preventDefault(); // Impede o envio se a validação falhar
            // }
        });
    }


// --- Nota sobre futuristic-cursor.js ---
// Se você tem um arquivo separado para o cursor futurista (futuristic-cursor.js),
// o código dele deve estar nesse arquivo e ser carregado separadamente no head_extra do index.html,
// como você já está fazendo. Não coloque o código do cursor aqui.
