let mainNav = document.getElementById("main-nav");
let navbarToggle = document.getElementById("navbar-toggle");

async function getuserParams() {
  try {
    let response = await fetch("/user/stats", {
      headers: {
        Authorization: "Bearer " + window.sessionStorage.getItem("jwt"),
      },
    });
    let data = await handleErrors(response).json();
    return data;
  } catch (error) {
    console.error(error.message);
  }
}

function handleErrors(response) {
  if (!response.ok) {
    throw Error(response.status + " " + response.statusText);
  }
  return response;
}

let response = await getuserParams();

navbarToggle.addEventListener("click", function () {
  if (this.classList.contains("active")) {
    mainNav.style.display = "none";
    this.classList.remove("active");
  } else {
    mainNav.style.display = "flex";
    this.classList.add("active");
  }
});

var xValues = [
  "A",
  "B",
  "C",
  "D",
  "E",
  "F",
  "G",
  "H",
  "I",
  "J",
  "K",
  "L",
  "M",
  "N",
  "Ñ",
  "O",
  "P",
  "Q",
  "R",
  "S",
  "T",
  "U",
  "V",
  "W",
  "X",
  "Y",
  "Z",
];

var yValues = [
  "A",
  "B",
  "C",
  "D",
  "E",
  "F",
  "G",
  "H",
  "I",
  "J",
  "K",
  "L",
  "M",
  "N",
  "Ñ",
  "O",
  "P",
  "Q",
  "R",
  "S",
  "T",
  "U",
  "V",
  "W",
  "X",
  "Y",
  "Z",
];

var zValues = response[0];

var data = [
  {
    x: xValues,
    y: yValues,
    z: zValues,
    type: "heatmap",
    colorscale: [
      [0, "green"],
      [0.5, "yellow"],
      [1, "red"],
    ],
  },
];

var barras = [
  {
    x: [
      "A",
      "B",
      "C",
      "D",
      "E",
      "F",
      "G",
      "H",
      "I",
      "J",
      "K",
      "L",
      "M",
      "N",
      "Ñ",
      "O",
      "P",
      "Q",
      "R",
      "S",
      "T",
      "U",
      "V",
      "W",
      "X",
      "Y",
      "Z",
    ],
    y: response[1],
    type: "bar",
  },
];

// Asignar colores en función de los valores
var coloresBarras = barras[0].y.map((valor) => {
  // Interpolación lineal para asignar colores en función del valor
  var escala = valor / 100; // Normalizar el valor entre 0 y 1
  var rojo = 255 * (1 - escala);
  var verde = 255 * escala;

  // Devolver el color en formato RGB
  return `rgb(${rojo}, ${verde}, 0)`;
});

barras[0].marker = {
  color: coloresBarras,
};

// Configurar el diseño del gráfico
var diseñoBarras = {
  title: "Porcentaje de efectividad",
  xaxis: {
    title: "Categorías",
  },
  yaxis: {
    title: "Valores",
  },
};

var layout = {
  title: "Tiempo entre pares de teclas",
  margin: { l: 50, r: 50, b: 50, t: 50, pad: 4 },
  xaxis: {
    tickangle: -45,
  },
};

Plotly.newPlot("divHeatMap", data, layout, { responsive: false });
Plotly.newPlot("divBarChart", barras, diseñoBarras, { responsive: false });