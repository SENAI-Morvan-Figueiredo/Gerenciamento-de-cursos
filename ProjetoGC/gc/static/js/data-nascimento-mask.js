// Máscara para campo de data de nascimento (DD/MM/YYYY)
document.addEventListener('DOMContentLoaded', function() {
    const dateInputs = document.querySelectorAll('input[data-date-mask="true"]');
    
    dateInputs.forEach(input => {
        // Evento de input para adicionar máscara
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, ''); // Remove tudo que não é dígito
            
            // Limita a 8 dígitos
            if (value.length > 8) {
                value = value.slice(0, 8);
            }
            
            // Formata como DD/MM/YYYY
            let formatted = '';
            if (value.length >= 1) {
                formatted = value.slice(0, 2);
            }
            if (value.length >= 3) {
                formatted += '/' + value.slice(2, 4);
            }
            if (value.length >= 5) {
                formatted += '/' + value.slice(4, 8);
            }
            
            e.target.value = formatted;
        });
        
        // Evento de blur para validação e conversão
        input.addEventListener('blur', function(e) {
            const value = e.target.value.trim();
            
            if (value.length === 0) {
                return; // Campo vazio é válido (pode ser obrigatório na validação do formulário)
            }
            
            // Valida o formato DD/MM/YYYY
            const regex = /^(\d{2})\/(\d{2})\/(\d{4})$/;
            const match = value.match(regex);
            
            if (!match) {
                e.target.classList.add('is-invalid');
                return;
            }
            
            const day = parseInt(match[1], 10);
            const month = parseInt(match[2], 10);
            const year = parseInt(match[3], 10);
            
            // Validação básica de datas
            if (month < 1 || month > 12) {
                e.target.classList.add('is-invalid');
                return;
            }
            
            if (day < 1 || day > 31) {
                e.target.classList.add('is-invalid');
                return;
            }
            
            // Validação de dias por mês
            const daysInMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
            
            // Verifica ano bissexto
            if ((year % 4 === 0 && year % 100 !== 0) || (year % 400 === 0)) {
                daysInMonth[1] = 29;
            }
            
            if (day > daysInMonth[month - 1]) {
                e.target.classList.add('is-invalid');
                return;
            }
            
            // Se passou por todas as validações, remove a classe de erro
            e.target.classList.remove('is-invalid');
            
            // Converte para formato YYYY-MM-DD para armazenar no campo oculto
            const isoDate = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
            const hiddenInput = document.querySelector(`input[name="data_nascimento_iso"]`);
            if (hiddenInput) {
                hiddenInput.value = isoDate;
            }
        });
        
        // Evento de keydown para controlar backspace
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Backspace' && e.target.value.length === 3) {
                // Remove a última barra e o dígito anterior
                e.target.value = e.target.value.slice(0, 2);
                e.preventDefault();
            } else if (e.key === 'Backspace' && e.target.value.length === 6) {
                // Remove a segunda barra
                e.target.value = e.target.value.slice(0, 5);
                e.preventDefault();
            }
        });
    });
});
