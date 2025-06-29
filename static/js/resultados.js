// Histograma
new Chart(document.getElementById('histograma'), {
    type: 'bar',
    data: {
        labels: labels,
        datasets: [{
            label: 'Frecuencia Absoluta (ni)',
            data: freqAbs,
            backgroundColor: 'rgba(54, 162, 235, 0.5)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        plugins: {
            title: { display: true, text: 'Histograma Frecuencia Absoluta' }
        },
        scales: {
            x: { title: { display: true, text: 'Marca de Clase (xi)' } },
            y: { title: { display: true, text: 'Frecuencia Absoluta' } }
        }
    }
});

// Polígono
new Chart(document.getElementById('poligono'), {
    type: 'line',
    data: {
        labels: labels,
        datasets: [{
            label: 'Polígono de Frecuencia',
            data: freqAbs,
            borderColor: 'rgba(255, 99, 132, 1)',
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            fill: false,
            tension: 0.1
        }]
    },
    options: {
        responsive: true,
        plugins: {
            title: { display: true, text: 'Polígono de Frecuencia' }
        },
        scales: {
            x: { title: { display: true, text: 'Marca de Clase (xi)' } },
            y: { title: { display: true, text: 'Frecuencia Absoluta' } }
        }
    }
});

// FI
new Chart(document.getElementById('fi'), {
    type: 'line',
    data: {
        labels: labels,
        datasets: [{
            label: 'FI',
            data: freqRelAcum,
            borderColor: 'rgba(75, 192, 192, 1)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            fill: false,
            tension: 0.1
        }]
    },
    options: {
        responsive: true,
        plugins: {
            title: { display: true, text: 'Frecuencia Relativa Acumulada (FI)' }
        },
        scales: {
            x: { title: { display: true, text: 'Marca de Clase (xi)' } },
            y: { title: { display: true, text: 'FI' } }
        }
    }
});

// FI Inversa
new Chart(document.getElementById('fiInversa'), {
    type: 'line',
    data: {
        labels: labels,
        datasets: [{
            label: 'FI Inversa',
            data: freqRelAcumInv,
            borderColor: 'rgba(153, 102, 255, 1)',
            backgroundColor: 'rgba(153, 102, 255, 0.2)',
            fill: false,
            tension: 0.1
        }]
    },
    options: {
        responsive: true,
        plugins: {
            title: { display: true, text: 'Frecuencia Relativa Acumulada Inversa' }
        },
        scales: {
            x: { title: { display: true, text: 'Marca de Clase (xi)' } },
            y: { title: { display: true, text: 'FI Inversa' } }
        }
    }
});
