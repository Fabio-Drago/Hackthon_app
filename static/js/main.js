// static/js/main.js

document.addEventListener('DOMContentLoaded', function() {
    // Script para fazer as mensagens flash desaparecerem automaticamente

    const flashContainer = document.querySelector('.flashes'); // Encontra o contêiner das mensagens flash

    if (flashContainer) {
        // Obtém todas as mensagens flash (li dentro do ul.flashes)
        const flashMessages = flashContainer.querySelectorAll('li');

        if (flashMessages.length > 0) {
            // Define o tempo em milissegundos para as mensagens desaparecerem (ex: 5000ms = 5 segundos)
            const timeout = 5000; // 5 segundos

            // Adiciona um timer para cada mensagem
            flashMessages.forEach(function(message) {
                setTimeout(function() {
                    // Adiciona uma classe para iniciar o fade-out (requer CSS) ou simplesmente esconde
                    // Vamos fazer um fade-out simples mudando a opacidade e depois escondendo
                    message.style.transition = 'opacity 0.5s ease-in-out'; // Adiciona transição
                    message.style.opacity = '0'; // Inicia o fade-out

                    // Remove o elemento do DOM depois que a transição terminar
                    // Ou após um pequeno atraso adicional se não usar transição
                    setTimeout(function() {
                        message.remove(); // Remove o elemento <li>
                    }, 500); // Tempo um pouco maior que a transição
                }, timeout); // Tempo total antes de iniciar o fade-out
            });
        }
    }

    // Você pode adicionar outros scripts gerais da sua aplicação aqui
    // ... (outro código JavaScript para funcionalidades gerais) ...

});