// static/js/logout_confirm.js

document.addEventListener('DOMContentLoaded', function() {
    const logoutLink = document.getElementById('logout-link');

    if (logoutLink) {
        logoutLink.addEventListener('click', function(event) {
            // Acessa as variáveis definidas globalmente no HTML pelo Jinja2
            // Usamos 'window.' para garantir que estamos acessando o escopo global
            const isParticipantAccountLoggedIn = window.IS_PARTICIPANT_LOGGED_IN;
            const hasRoomSession = window.HAS_ROOM_SESSION;

            let confirmMessage = 'Tem certeza que deseja sair?';

            // Determina a mensagem de confirmação com base no status
            if (isParticipantAccountLoggedIn && hasRoomSession) {
                confirmMessage = 'Tem certeza que deseja sair da sala? Seu progresso atual (respostas não salvas) pode ser perdido.';
            } else if (isParticipantAccountLoggedIn) {
                confirmMessage = 'Tem certeza que deseja sair da sua conta?';
            }
            // Para admin, a mensagem padrão 'Tem certeza que deseja sair?' é usada.

            if (!confirm(confirmMessage)) {
                event.preventDefault(); // Impede a navegação se o usuário cancelar
            }
        });
    }
});