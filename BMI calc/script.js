/* =========================================================
   VITALTRACK JAVASCRIPT
========================================================= */


/* =========================================================
   DATA
========================================================= */

let historyData = [

    {
        date: "02 Sep 2026",
        weight: 68.0,
        height: 1.74,
        bmi: 22.45,
        status: "Normal"
    },

    {
        date: "25 Aug 2026",
        weight: 69.2,
        height: 1.74,
        bmi: 22.86,
        status: "Normal"
    },

    {
        date: "18 Aug 2026",
        weight: 70.0,
        height: 1.74,
        bmi: 23.12,
        status: "Normal"
    },

    {
        date: "10 Aug 2026",
        weight: 71.0,
        height: 1.74,
        bmi: 23.45,
        status: "Normal"
    },

    {
        date: "01 Aug 2026",
        weight: 72.0,
        height: 1.74,
        bmi: 23.78,
        status: "Normal"
    }

];


/* =========================================================
   DOM
========================================================= */

const navItems = document.querySelectorAll(".nav-item");

const pages = document.querySelectorAll(".page");

const pageTitle = document.getElementById("pageTitle");

const sidebar = document.getElementById("sidebar");

const mobileMenu = document.getElementById("mobileMenu");

const toast = document.getElementById("toast");


/* =========================================================
   PAGE NAVIGATION
========================================================= */

function showPage(pageName) {

    pages.forEach(page => {

        page.classList.remove("active-page");

    });


    const targetPage = document.getElementById(pageName);

    if (targetPage) {

        targetPage.classList.add("active-page");

    }


    navItems.forEach(item => {

        item.classList.remove("active");

        if (item.dataset.page === pageName) {

            item.classList.add("active");

        }

    });


    const titles = {

        dashboard: "Dashboard",

        calculator: "BMI Calculator",

        history: "BMI History",

        trends: "BMI Trends",

        profiles: "Profiles",

        settings: "Settings"

    };


    pageTitle.textContent = titles[pageName] || "VitalTrack";


    sidebar.classList.remove("open");


    if (pageName === "history") {

        renderHistory();

    }


    if (pageName === "trends") {

        setTimeout(() => {

            createTrendChart();

        }, 100);

    }

}


/* =========================================================
   NAV CLICK
========================================================= */

navItems.forEach(item => {

    item.addEventListener("click", () => {

        showPage(item.dataset.page);

    });

});


/* =========================================================
   OTHER PAGE BUTTONS
========================================================= */

document.querySelectorAll("[data-page]").forEach(button => {

    if (!button.classList.contains("nav-item")) {

        button.addEventListener("click", () => {

            showPage(button.dataset.page);

        });

    }

});


/* =========================================================
   MOBILE MENU
========================================================= */

mobileMenu.addEventListener("click", () => {

    sidebar.classList.toggle("open");

});


/* =========================================================
   BMI CALCULATION
========================================================= */

function calculateBMI(weight, height) {

    if (!weight || !height) {

        return null;

    }


    if (weight <= 0 || height <= 0) {

        return null;

    }


    return weight / (height * height);

}


/* =========================================================
   BMI CATEGORY
========================================================= */

function getCategory(bmi) {

    if (bmi < 18.5) {

        return {
            name: "Underweight",
            className: "underweight",
            color: "#4f8cff",
            description:
                "Your BMI is below the standard healthy range."
        };

    }


    if (bmi < 25) {

        return {
            name: "Normal",
            className: "normal",
            color: "#22c55e",
            description:
                "You're currently within the healthy BMI range."
        };

    }


    if (bmi < 30) {

        return {
            name: "Overweight",
            className: "overweight",
            color: "#f97316",
            description:
                "Your BMI is above the standard healthy range."
        };

    }


    return {
        name: "Obese",
        className: "obese",
        color: "#ef4444",
        description:
            "Your BMI is in the obese category."
    };

}


/* =========================================================
   BMI SCALE
========================================================= */

function getScalePosition(bmi) {

    let position;


    if (bmi < 18.5) {

        position = (bmi / 18.5) * 25;

    }

    else if (bmi < 25) {

        position = 25 +
            ((bmi - 18.5) / 6.5) * 25;

    }

    else if (bmi < 30) {

        position = 50 +
            ((bmi - 25) / 5) * 25;

    }

    else {

        position = 75 +
            Math.min(((bmi - 30) / 10) * 25, 25);

    }


    return Math.max(
        2,
        Math.min(position, 98)
    );

}


/* =========================================================
   UPDATE DASHBOARD
========================================================= */

function updateDashboard(bmi, category) {

    document.getElementById("bmiNumber").textContent =
        bmi.toFixed(2);


    const status = document.getElementById("bmiStatus");

    status.textContent =
        `● ${category.name.toUpperCase()}`;


    status.className =
        `status ${category.className}`;


    document.getElementById("resultDescription")
        .textContent = category.description;


    document.getElementById("dashboardBMI")
        .textContent = bmi.toFixed(2);


    const dashboardStatus =
        document.getElementById("dashboardStatus");

    dashboardStatus.textContent =
        category.name;


    document.getElementById("scaleIndicator")
        .style.left =
        `${getScalePosition(bmi)}%`;

}


/* =========================================================
   DASHBOARD CALCULATOR
========================================================= */

document.getElementById("calculateBtn")
    .addEventListener("click", () => {

        const weight =
            parseFloat(
                document.getElementById("weight").value
            );


        const height =
            parseFloat(
                document.getElementById("height").value
            );


        const bmi =
            calculateBMI(weight, height);


        if (!bmi) {

            showToast(
                "Please enter valid positive values."
            );

            return;

        }


        const category =
            getCategory(bmi);


        updateDashboard(
            bmi,
            category
        );


        addRecord(
            weight,
            height,
            bmi,
            category.name
        );


        showToast(
            `BMI calculated: ${bmi.toFixed(2)}`
        );

    });


/* =========================================================
   SEPARATE CALCULATOR
========================================================= */

document.getElementById("calculateSeparate")
    .addEventListener("click", () => {

        const weight =
            parseFloat(
                document.getElementById("calcWeight").value
            );


        const height =
            parseFloat(
                document.getElementById("calcHeight").value
            );


        const output =
            document.getElementById("calculatorOutput");


        const bmi =
            calculateBMI(weight, height);


        if (!bmi) {

            output.textContent =
                "Please enter valid positive values.";

            output.style.color =
                "#ef4444";

            return;

        }


        const category =
            getCategory(bmi);


        output.innerHTML = `

            <div>

                <div style="
                    font-size: 42px;
                    font-weight: 800;
                    margin-bottom: 8px;
                ">
                    ${bmi.toFixed(2)}
                </div>

                <div style="
                    color: ${category.color};
                    font-weight: 800;
                    font-size: 14px;
                ">
                    ● ${category.name.toUpperCase()}
                </div>

            </div>

        `;

        output.style.color =
            category.color;

    });


/* =========================================================
   ADD RECORD
========================================================= */

function addRecord(
    weight,
    height,
    bmi,
    status
) {

    const today =
        new Date();


    const formattedDate =
        today.toLocaleDateString(
            "en-GB",
            {
                day: "2-digit",
                month: "short",
                year: "numeric"
            }
        );


    historyData.unshift({

        date: formattedDate,

        weight: weight,

        height: height,

        bmi: bmi,

        status: status

    });


    updateRecordCount();

}


/* =========================================================
   RECORD COUNT
========================================================= */

function updateRecordCount() {

    document.getElementById(
        "recordCount"
    ).textContent =
        historyData.length;


    document.getElementById(
        "profileRecords"
    ).textContent =
        historyData.length;

}


/* =========================================================
   HISTORY TABLE
========================================================= */

function renderHistory() {

    const table =
        document.getElementById(
            "historyTable"
        );


    table.innerHTML = "";


    historyData.forEach(record => {

        const row =
            document.createElement("tr");


        const statusClass =
            record.status === "Normal"
                ? "status-cell"
                : "";


        row.innerHTML = `

            <td>${record.date}</td>

            <td>${record.weight.toFixed(1)} kg</td>

            <td>${record.height.toFixed(2)} m</td>

            <td>${record.bmi.toFixed(2)}</td>

            <td class="${statusClass}">
                ${record.status}
            </td>

        `;


        table.appendChild(row);

    });

}


/* =========================================================
   CHART DATA
========================================================= */

function getChartLabels() {

    return [...historyData]
        .reverse()
        .map(record => record.date);

}


function getChartValues() {

    return [...historyData]
        .reverse()
        .map(record => record.bmi);

}


/* =========================================================
   DASHBOARD CHART
========================================================= */

let dashboardChart;


function createDashboardChart() {

    const canvas =
        document.getElementById(
            "dashboardChart"
        );


    if (!canvas) return;


    const ctx =
        canvas.getContext("2d");


    if (dashboardChart) {

        dashboardChart.destroy();

    }


    dashboardChart =
        new Chart(
            ctx,
            {

                type: "line",

                data: {

                    labels:
                        getChartLabels(),

                    datasets: [

                        {

                            data:
                                getChartValues(),

                            borderColor:
                                "#4f8cff",

                            backgroundColor:
                                "rgba(79,140,255,0.08)",

                            fill: true,

                            tension: 0.4,

                            pointRadius: 4,

                            pointBackgroundColor:
                                "#4f8cff"

                        }

                    ]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    plugins: {

                        legend: {
                            display: false
                        }

                    },

                    scales: {

                        x: {

                            grid: {
                                display: false
                            },

                            ticks: {
                                color: "#94a3b8"
                            }

                        },

                        y: {

                            min: 20,

                            max: 26,

                            ticks: {
                                color: "#94a3b8"
                            },

                            grid: {
                                color:
                                    "rgba(148,163,184,0.08)"
                            }

                        }

                    }

                }

            }

        );

}


/* =========================================================
   FULL TREND CHART
========================================================= */

let trendChart;


function createTrendChart() {

    const canvas =
        document.getElementById(
            "trendChart"
        );


    if (!canvas) return;


    const ctx =
        canvas.getContext("2d");


    if (trendChart) {

        trendChart.destroy();

    }


    trendChart =
        new Chart(
            ctx,
            {

                type: "line",

                data: {

                    labels:
                        getChartLabels(),

                    datasets: [

                        {

                            label: "BMI",

                            data:
                                getChartValues(),

                            borderColor:
                                "#4f8cff",

                            backgroundColor:
                                "rgba(79,140,255,0.1)",

                            fill: true,

                            tension: 0.4,

                            pointRadius: 5,

                            pointHoverRadius: 8

                        }

                    ]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    plugins: {

                        legend: {

                            labels: {
                                color: "#94a3b8"
                            }

                        }

                    },

                    scales: {

                        x: {

                            ticks: {
                                color: "#94a3b8"
                            },

                            grid: {
                                display: false
                            }

                        },

                        y: {

                            ticks: {
                                color: "#94a3b8"
                            },

                            grid: {
                                color:
                                    "rgba(148,163,184,0.08)"
                            }

                        }

                    }

                }

            }

        );

}


/* =========================================================
   TOAST
========================================================= */

function showToast(message) {

    toast.textContent =
        message;


    toast.classList.add(
        "show"
    );


    setTimeout(() => {

        toast.classList.remove(
            "show"
        );

    }, 2500);

}


/* =========================================================
   THEME
========================================================= */

document.querySelectorAll(
    ".theme-btn"
).forEach(button => {

    button.addEventListener(
        "click",
        () => {

            const theme =
                button.dataset.theme;


            document.body.classList.toggle(
                "light",
                theme === "light"
            );


            document.querySelectorAll(
                ".theme-btn"
            ).forEach(btn => {

                btn.classList.remove(
                    "active"
                );

            });


            button.classList.add(
                "active"
            );

        }
    );

});


/* =========================================================
   KEYBOARD ENTER SUPPORT
========================================================= */

document.querySelectorAll(
    "input"
).forEach(input => {

    input.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "Enter"
            ) {

                document.getElementById(
                    "calculateBtn"
                ).click();

            }

        }
    );

});


/* =========================================================
   INITIALIZE
========================================================= */

renderHistory();

updateRecordCount();

createDashboardChart();
