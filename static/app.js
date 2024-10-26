document.getElementById("swap-btn").addEventListener("click", function() {
    let fromCurrency = document.getElementById("from_currency");
    let toCurrency = document.getElementById("to_currency");

    let temp = fromCurrency.value;
    fromCurrency.value = toCurrency.value;
    toCurrency.value = temp;
});
