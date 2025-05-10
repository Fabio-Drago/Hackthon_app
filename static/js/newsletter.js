// static/js/newsletter.js
// Este arquivo agora contém apenas scripts utilitários gerais que podem ser usados em várias partes
// da aplicação.
// A lógica específica da landing page (submissão do formulário, contador regressivo,
// exibição de flash messages como toasts) foi movida para o script no index.html.

document.addEventListener('DOMContentLoaded', function() {
    // Código a ser executado após o DOM ser completamente carregado.

    /**
     * Valida formato de email.
     * Mantida aqui se você precisar dela em outros formulários ou partes do seu site.
     * Se não, pode ser removida.
     */
    function validateEmail(email) {
        const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(String(email).toLowerCase());
    }

    // Removido: Lógica original de submissão do formulário via fetch.
    // Removido: Funções showSuccessMessage, createToast, sendConfirmationEmail (duplicadas ou não usadas).
    // Removido: Lógica do contador regressivo (movida para o index.html).
    // Removido: Código para adicionar estilos CSS (deve estar em arquivo .css ou no template).

    // Adicione outras funções JavaScript reutilizáveis aqui, se necessário.

});

// Se você definir funções globais aqui para usar em outros scripts,
// declare-as fora do DOMContentLoaded ou anexe-as ao objeto window.
// Exemplo: window.validateEmail = validateEmail;