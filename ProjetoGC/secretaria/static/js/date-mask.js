// static/js/date-mask.js

// Função para aplicar máscara de data durante a digitação
function applyDateMask(input) {
  let value = input.value.replace(/\D/g, ""); // Remove tudo que não é número
  let formattedValue = "";

  // Aplica a máscara: DD/MM/YYYY
  if (value.length > 0) {
    formattedValue = value.substring(0, 2);
    if (value.length > 2) {
      formattedValue += "/" + value.substring(2, 4);
      if (value.length > 4) {
        formattedValue += "/" + value.substring(4, 8);
      }
    }
  }

  input.value = formattedValue;
}

// Função para validar teclas pressionadas (apenas números e teclas de controle)
function dateMask(event) {
  const charCode = event.which ? event.which : event.keyCode;
  const input = event.target;
  const value = input.value;

  // Permite teclas de controle: backspace, delete, tab, etc.
  if (
    charCode === 8 ||
    charCode === 9 ||
    charCode === 46 ||
    (charCode >= 37 && charCode <= 40)
  ) {
    return true;
  }

  // Permite apenas números
  if (charCode < 48 || charCode > 57) {
    return false;
  }

  // Não permite mais de 10 caracteres (DD/MM/YYYY)
  if (value.replace(/\D/g, "").length >= 8) {
    return false;
  }

  return true;
}

// Função para formatar todos os campos de data na página
function initializeDateMasks() {
  const dateInputs = document.querySelectorAll(
    '.date-input, input[type="text"][placeholder*="DD/MM"]'
  );

  dateInputs.forEach((input) => {
    // Adiciona os eventos se não existirem
    if (!input.hasAttribute("data-mask-initialized")) {
      input.addEventListener("input", function (e) {
        applyDateMask(this);
      });

      input.addEventListener("keypress", function (e) {
        return dateMask(e);
      });

      input.addEventListener("blur", function (e) {
        validateDate(this);
      });

      input.setAttribute("data-mask-initialized", "true");
    }
  });
}

// Função para validar a data após sair do campo
function validateDate(input) {
  const value = input.value;

  if (!value) return;

  // Verifica se tem o formato correto
  if (!/^\d{2}\/\d{2}\/\d{4}$/.test(value)) {
    input.style.borderColor = "red";
    return;
  }

  // Valida dia, mês e ano
  const parts = value.split("/");
  const day = parseInt(parts[0], 10);
  const month = parseInt(parts[1], 10);
  const year = parseInt(parts[2], 10);

  // Validações básicas
  if (
    day < 1 ||
    day > 31 ||
    month < 1 ||
    month > 12 ||
    year < 1900 ||
    year > 2100
  ) {
    input.style.borderColor = "red";
    return;
  }

  // Verifica se é uma data válida
  const date = new Date(year, month - 1, day);
  if (
    date.getFullYear() !== year ||
    date.getMonth() + 1 !== month ||
    date.getDate() !== day
  ) {
    input.style.borderColor = "red";
    return;
  }

  input.style.borderColor = "";
}

// Inicializa quando o DOM estiver carregado
document.addEventListener("DOMContentLoaded", function () {
  initializeDateMasks();
});

// Também inicializa quando o conteúdo é carregado dinamicamente
document.addEventListener("turbolinks:load", initializeDateMasks); // Para Turbolinks
document.addEventListener("ajaxComplete", initializeDateMasks); // Para AJAX
