const ratingCanvas = document.getElementById("ratingsChart");
new Chart(ratingCanvas, {
  type: "bar",
  data: {
    labels: ["1 star", "2 stars", "3 stars", "4 stars", "5 stars"],
    datasets: [{
      label: "Number of ratings",
      data: [13406072, 30997156, 114758938, 199656966, 237898056],
      backgroundColor: ["#a9b8a5", "#91aa92", "#789b7e", "#527b60", "#315c49"],
      borderRadius: 6
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      y: {
        beginAtZero: true,
        ticks: { callback: value => (value / 1000000) + "M" }
      }
    }
  }
});

const authorsCanvas = document.getElementById("authorsChart");
new Chart(authorsCanvas, {
  type: "bar",
  data: {
    labels: [
      "James Patterson", "Stephen King", "Nora Roberts", "Dean Koontz",
      "Terry Pratchett", "Agatha Christie", "J.D. Robb", "Neil Gaiman",
      "Meg Cabot", "Janet Evanovich"
    ],
    datasets: [{
      label: "Book count",
      data: [98, 97, 65, 64, 50, 43, 41, 41, 38, 37],
      backgroundColor: "#527b60",
      borderRadius: 5
    }]
  },
  options: {
    indexAxis: "y",
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: { x: { beginAtZero: true } }
  }
});
