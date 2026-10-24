document.addEventListener("DOMContentLoaded", function () {

    // ============================================================
    // MAP SETUP
    // ============================================================

    const map = L.map("map").setView([12.37, 75.77], 11);

    // Use OpenStreetMap directly.
    // This removes the CARTO API-key problem.
    L.tileLayer(
        "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        {
            maxZoom: 19,
            attribution:
                '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors'
        }
    ).addTo(map);


    // ============================================================
    // BUTTONS
    // ============================================================

    const findRouteButton =
        document.getElementById("findRouteButton");

    const simulationButton =
        document.getElementById("simulationButton");

    const resetSimulationButton =
        document.getElementById("resetSimulationButton");


    // ============================================================
    // LEGEND
    // ============================================================

    let riskLegend = null;


    // ============================================================
    // ROUTE COORDINATES
    // ============================================================

    function getRouteCoordinates() {

        const startLat =
            parseFloat(
                document.getElementById("startLat").value
            );

        const startLon =
            parseFloat(
                document.getElementById("startLon").value
            );

        const endLat =
            parseFloat(
                document.getElementById("endLat").value
            );

        const endLon =
            parseFloat(
                document.getElementById("endLon").value
            );


        if (
            Number.isNaN(startLat) ||
            Number.isNaN(startLon) ||
            Number.isNaN(endLat) ||
            Number.isNaN(endLon)
        ) {

            alert(
                "Please enter valid coordinates."
            );

            return null;
        }


        return {

            start_lat: startLat,

            start_lon: startLon,

            end_lat: endLat,

            end_lon: endLon
        };
    }


    // ============================================================
    // SIMULATION WEATHER
    // ============================================================

    function getSimulationWeather() {

        return {

            rainfall:
                parseFloat(
                    document.getElementById(
                        "simulationRainfall"
                    ).value
                ),

            rainfall_6h:
                parseFloat(
                    document.getElementById(
                        "simulationRainfall6h"
                    ).value
                ),

            rainfall_12h:
                parseFloat(
                    document.getElementById(
                        "simulationRainfall12h"
                    ).value
                ),

            rainfall_24h:
                parseFloat(
                    document.getElementById(
                        "simulationRainfall24h"
                    ).value
                ),

            humidity:
                parseFloat(
                    document.getElementById(
                        "simulationHumidity"
                    ).value
                ),

            temperature:
                parseFloat(
                    document.getElementById(
                        "simulationTemperature"
                    ).value
                )
        };
    }


    // ============================================================
    // RISK COLORS
    // ============================================================

    function getRiskColor(level) {

        if (level === "VERY HIGH") {
            return "#800080";
        }

        if (level === "HIGH") {
            return "#ff0000";
        }

        if (level === "MEDIUM") {
            return "#ff9900";
        }

        return "#00aa44";
    }


    // ============================================================
    // CLEAR MAP ROUTES
    // ============================================================

    function clearMapRoutes() {

        map.eachLayer(function (layer) {

            if (
                layer instanceof L.Polyline ||
                layer instanceof L.Marker ||
                layer instanceof L.CircleMarker
            ) {

                map.removeLayer(layer);
            }

        });
    }


    // ============================================================
    // MAP LEGEND
    // ============================================================

    function addLegend() {

        if (riskLegend !== null) {

            map.removeControl(
                riskLegend
            );
        }


        const legend =
            L.control({
                position: "bottomright"
            });


        legend.onAdd =
            function () {

                const div =
                    L.DomUtil.create(
                        "div",
                        "info legend"
                    );


                div.style.background =
                    "white";

                div.style.padding =
                    "12px";

                div.style.borderRadius =
                    "8px";

                div.style.boxShadow =
                    "0 1px 5px rgba(0,0,0,0.3)";


                div.innerHTML = `

                    <strong>
                        LANDSLIDE RISK
                    </strong>

                    <div style="margin-top:8px;">
                        <span style="
                            display:inline-block;
                            width:18px;
                            height:18px;
                            background:#00aa44;
                            margin-right:6px;
                            vertical-align:middle;
                        "></span>
                        LOW
                    </div>

                    <div>
                        <span style="
                            display:inline-block;
                            width:18px;
                            height:18px;
                            background:#ff9900;
                            margin-right:6px;
                            vertical-align:middle;
                        "></span>
                        MEDIUM
                    </div>

                    <div>
                        <span style="
                            display:inline-block;
                            width:18px;
                            height:18px;
                            background:#ff0000;
                            margin-right:6px;
                            vertical-align:middle;
                        "></span>
                        HIGH
                    </div>

                    <div>
                        <span style="
                            display:inline-block;
                            width:18px;
                            height:18px;
                            background:#800080;
                            margin-right:6px;
                            vertical-align:middle;
                        "></span>
                        VERY HIGH
                    </div>

                    <hr>

                    <div>
                        <span style="
                            display:inline-block;
                            width:25px;
                            border-top:5px solid #0066ff;
                            margin-right:6px;
                            vertical-align:middle;
                        "></span>
                        RECOMMENDED ROUTE
                    </div>

                `;


                return div;
            };


        legend.addTo(map);

        riskLegend = legend;
    }


    // ============================================================
    // DRAW ROUTES
    // ============================================================

    function drawRoutes(
        routes,
        startLat,
        startLon,
        endLat,
        endLon
    ) {

        clearMapRoutes();


        // ========================================================
        // BLUE RECOMMENDED ROUTE UNDERLAY
        // ========================================================

        routes.forEach(
            function (route) {

                if (!route.recommended) {
                    return;
                }


                const recommendedLine =
                    L.polyline(
                        route.geometry,
                        {
                            color: "#0066ff",

                            weight: 12,

                            opacity: 0.95,

                            lineCap: "round",

                            lineJoin: "round"
                        }
                    );


                recommendedLine.addTo(map);
            }
        );


        // ========================================================
        // RISK SEGMENTS
        // ========================================================

        routes.forEach(
            function (route) {

                if (
                    !route.segments ||
                    route.segments.length === 0
                ) {

                    return;
                }


                route.segments.forEach(
                    function (segment) {

                        const riskColor =
                            getRiskColor(
                                segment.level
                            );


                        const line =
                            L.polyline(
                                [
                                    [
                                        segment.start.lat,
                                        segment.start.lon
                                    ],

                                    [
                                        segment.end.lat,
                                        segment.end.lon
                                    ]
                                ],
                                {
                                    color: riskColor,

                                    weight:
                                        route.recommended
                                            ? 8
                                            : 5,

                                    opacity:
                                        route.recommended
                                            ? 1
                                            : 0.65,

                                    lineCap: "round",

                                    lineJoin: "round"
                                }
                            );


                        // ========================================
                        // SEGMENT POPUP
                        // ========================================

                        line.bindPopup(`

                            <div style="
                                min-width:220px;
                                font-family:Arial,sans-serif;
                            ">

                                <h3 style="
                                    margin-top:0;
                                    color:#163c35;
                                ">
                                    Route ${route.route_id}
                                </h3>

                                <p>
                                    <b>Segment:</b>
                                    ${segment.segment_id}
                                </p>

                                <p>
                                    <b>Risk:</b>
                                    ${segment.risk}%
                                </p>

                                <p>
                                    <b>Risk Level:</b>
                                    ${segment.level}
                                </p>

                                <p>
                                    <b>Slope:</b>
                                    ${segment.slope}°
                                </p>

                                <p>
                                    <b>Elevation:</b>
                                    ${segment.elevation} m
                                </p>

                                <p>
                                    <b>ML Risk:</b>
                                    ${segment.ml_risk}%
                                </p>

                                <p>
                                    <b>Rainfall Risk:</b>
                                    ${segment.rainfall_risk}%
                                </p>

                                <p>
                                    <b>Interaction Risk:</b>
                                    ${segment.interaction_risk}%
                                </p>

                            </div>

                        `);


                        line.addTo(map);
                    }
                );
            }
        );


        // ========================================================
        // START MARKER
        // ========================================================

        L.marker(
            [
                startLat,
                startLon
            ]
        )
        .bindPopup(
            "<b>START LOCATION</b>"
        )
        .addTo(map);


        // ========================================================
        // DESTINATION MARKER
        // ========================================================

        L.marker(
            [
                endLat,
                endLon
            ]
        )
        .bindPopup(
            "<b>DESTINATION</b>"
        )
        .addTo(map);


        // ========================================================
        // FIT MAP
        // ========================================================

        const allPoints = [];


        routes.forEach(
            function (route) {

                if (
                    !route.geometry ||
                    route.geometry.length === 0
                ) {

                    return;
                }


                route.geometry.forEach(
                    function (point) {

                        allPoints.push(
                            point
                        );
                    }
                );
            }
        );


        if (allPoints.length > 0) {

            map.fitBounds(
                allPoints,
                {
                    padding: [
                        30,
                        30
                    ]
                }
            );
        }


        addLegend();
    }


    // ============================================================
    // UPDATE RESULTS
    // ============================================================

    function updateResults(
        recommendedRoute,
        weather,
        routes
    ) {

        // ========================================================
        // BASIC RESULTS
        // ========================================================

        document.getElementById(
            "riskLevel"
        ).innerText =
            recommendedRoute.risk_level;


        document.getElementById(
            "riskScore"
        ).innerText =
            recommendedRoute.average_risk +
            "%";


        document.getElementById(
            "distance"
        ).innerText =
            recommendedRoute.distance_km +
            " km";


        document.getElementById(
            "duration"
        ).innerText =
            recommendedRoute.duration_min +
            " min";


        // ========================================================
        // WEATHER
        // ========================================================

        if (weather) {

            document.getElementById(
                "rainfall"
            ).innerText =
                weather.rainfall +
                " mm";


            document.getElementById(
                "humidity"
            ).innerText =
                weather.humidity +
                "%";


            document.getElementById(
                "temperature"
            ).innerText =
                weather.temperature +
                " °C";
        }


        // ========================================================
        // TERRAIN
        // ========================================================

        if (
            recommendedRoute.segments &&
            recommendedRoute.segments.length > 0
        ) {

            const firstSegment =
                recommendedRoute.segments[0];


            document.getElementById(
                "elevation"
            ).innerText =
                firstSegment.elevation +
                " m";


            document.getElementById(
                "slope"
            ).innerText =
                firstSegment.slope +
                "°";
        }


        // ========================================================
        // ROUTE COMPARISON
        // ========================================================

        const comparison =
            document.getElementById(
                "routeComparison"
            );


        comparison.innerHTML = "";


        // ========================================================
        // SAFEST ROUTE RECOMMENDATION
        // ========================================================

        const recommendation =
            document.createElement(
                "div"
            );


        recommendation.style.padding =
            "18px";

        recommendation.style.marginBottom =
            "15px";

        recommendation.style.border =
            "3px solid #0066ff";

        recommendation.style.borderRadius =
            "12px";

        recommendation.style.background =
            "#f4f8ff";


        recommendation.innerHTML = `

            <h2 style="
                margin-top:0;
                color:#0066ff;
            ">
                ⭐ SAFEST ROUTE
            </h2>

            <h3>
                Route ${recommendedRoute.route_id}
            </h3>

            <p>
                <b>Safety Score:</b>
                ${recommendedRoute.safety_score}/100
            </p>

            <p>
                <b>Average Risk:</b>
                ${recommendedRoute.average_risk}%
            </p>

            <p>
                <b>Maximum Risk:</b>
                ${recommendedRoute.maximum_risk}%
            </p>

            <p>
                <b>Distance:</b>
                ${recommendedRoute.distance_km} km
            </p>

            <p>
                <b>Estimated Time:</b>
                ${recommendedRoute.duration_min} min
            </p>

            <p style="
                margin-bottom:0;
                font-weight:bold;
            ">
                SafePath AI recommends this route
                based on the current risk analysis.
            </p>

        `;


        comparison.appendChild(
            recommendation
        );


        // ========================================================
        // ROUTE CARDS
        // ========================================================

        routes.forEach(
            function (route) {

                const card =
                    document.createElement(
                        "div"
                    );


                card.style.padding =
                    "15px";

                card.style.marginBottom =
                    "10px";

                card.style.border =
                    "1px solid #ddd";

                card.style.borderRadius =
                    "10px";


                if (route.recommended) {

                    card.style.border =
                        "3px solid #0066ff";

                    card.style.background =
                        "#f4f8ff";
                }


                const title =
                    route.recommended
                        ? "⭐ ROUTE " +
                          route.route_id +
                          " — RECOMMENDED"

                        : "ROUTE " +
                          route.route_id;


                const dangerous =
                    route.dangerous_segment_percentage ??
                    0;


                const summary =
                    route.segment_summary || {
                        low: 0,
                        medium: 0,
                        high: 0,
                        very_high: 0
                    };


                card.innerHTML = `

                    <h3>
                        ${title}
                    </h3>

                    <p>
                        <b>Risk Level:</b>
                        ${route.risk_level}
                    </p>

                    <p>
                        <b>Average Risk:</b>
                        ${route.average_risk}%
                    </p>

                    <p>
                        <b>Maximum Risk:</b>
                        ${route.maximum_risk}%
                    </p>

                    <p>
                        <b>Safety Score:</b>
                        ${route.safety_score}
                    </p>

                    <p>
                        <b>Dangerous Segments:</b>
                        ${dangerous}%
                    </p>

                    <p>
                        <b>Distance:</b>
                        ${route.distance_km} km
                    </p>

                    <p>
                        <b>Time:</b>
                        ${route.duration_min} min
                    </p>

                    <p>
                        <b>LOW:</b>
                        ${summary.low}

                        &nbsp;&nbsp;

                        <b>MEDIUM:</b>
                        ${summary.medium}

                        &nbsp;&nbsp;

                        <b>HIGH:</b>
                        ${summary.high}

                        &nbsp;&nbsp;

                        <b>VERY HIGH:</b>
                        ${summary.very_high}
                    </p>

                `;


                comparison.appendChild(
                    card
                );
            }
        );
    }


    // ============================================================
    // MAIN ANALYSIS
    // ============================================================

    async function analyzeRoute(
        simulationMode = false
    ) {

        const coordinates =
            getRouteCoordinates();


        if (!coordinates) {
            return;
        }


        // ========================================================
        // BUTTON STATE
        // ========================================================

        if (simulationMode) {

            simulationButton.disabled =
                true;

            simulationButton.innerText =
                "SIMULATING...";

        }
        else {

            findRouteButton.disabled =
                true;

            findRouteButton.innerText =
                "ANALYZING ROUTES...";
        }


        try {

            // ====================================================
            // REQUEST BODY
            // ====================================================

            let requestBody = {
                ...coordinates
            };


            if (simulationMode) {

                const simulation =
                    getSimulationWeather();


                requestBody = {
                    ...requestBody,
                    ...simulation
                };
            }


            console.log(
                "SafePath AI Request:",
                requestBody
            );


            // ====================================================
            // BACKEND REQUEST
            // ====================================================

            const response =
                await fetch(
                    "http://127.0.0.1:8000/route-segments",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(
                                requestBody
                            )
                    }
                );


            if (!response.ok) {

                throw new Error(
                    "Backend request failed. HTTP " +
                    response.status
                );
            }


            const data =
                await response.json();


            console.log(
                "SafePath AI Response:",
                data
            );


            // ====================================================
            // ROUTES
            // ====================================================

            const routes =
                data.routes &&
                data.routes.routes
                    ? data.routes.routes
                    : null;


            if (
                !routes ||
                routes.length === 0
            ) {

                throw new Error(
                    "No routes returned by backend."
                );
            }


            // ====================================================
            // RECOMMENDED ROUTE
            // ====================================================

            let recommendedRoute =
                routes.find(
                    function (route) {

                        return (
                            route.recommended === true
                        );
                    }
                );


            if (!recommendedRoute) {

                recommendedRoute =
                    routes[0];
            }


            // ====================================================
            // WEATHER
            // ====================================================

            const weather =
                data.weather ||
                data.routes.weather;


            if (!weather) {

                console.warn(
                    "Weather data was not returned."
                );
            }


            // ====================================================
            // DRAW MAP
            // ====================================================

            drawRoutes(
                routes,

                coordinates.start_lat,
                coordinates.start_lon,

                coordinates.end_lat,
                coordinates.end_lon
            );


            // ====================================================
            // UPDATE RESULTS
            // ====================================================

            updateResults(
                recommendedRoute,
                weather,
                routes
            );


            // ====================================================
            // UPDATE SIMULATION INPUTS
            // ====================================================

            if (
                !simulationMode &&
                weather
            ) {

                document.getElementById(
                    "simulationRainfall"
                ).value =
                    weather.rainfall ?? 0;


                document.getElementById(
                    "simulationRainfall6h"
                ).value =
                    weather.rainfall_6h ?? 0;


                document.getElementById(
                    "simulationRainfall12h"
                ).value =
                    weather.rainfall_12h ?? 0;


                document.getElementById(
                    "simulationRainfall24h"
                ).value =
                    weather.rainfall_24h ?? 0;


                document.getElementById(
                    "simulationHumidity"
                ).value =
                    weather.humidity ?? 0;


                document.getElementById(
                    "simulationTemperature"
                ).value =
                    weather.temperature ?? 0;
            }


            // ====================================================
            // CONSOLE
            // ====================================================

            console.log(
                "================================"
            );

            console.log(
                "SafePath AI Analysis Complete"
            );

            console.log(
                "Simulation:",
                simulationMode
            );

            console.log(
                "Recommended Route:",
                recommendedRoute.route_id
            );

            console.log(
                "Risk Level:",
                recommendedRoute.risk_level
            );

            console.log(
                "Average Risk:",
                recommendedRoute.average_risk
            );

            console.log(
                "Maximum Risk:",
                recommendedRoute.maximum_risk
            );

            console.log(
                "Safety Score:",
                recommendedRoute.safety_score
            );

            console.log(
                "================================"
            );
        }


        catch (error) {

            console.error(
                "SafePath AI Error:",
                error
            );


            alert(
                "Unable to analyze routes.\n\n" +
                error.message +
                "\n\n" +
                "Make sure the backend is running."
            );
        }


        finally {

            if (simulationMode) {

                simulationButton.disabled =
                    false;

                simulationButton.innerText =
                    "ANALYZE SIMULATION";

            }
            else {

                findRouteButton.disabled =
                    false;

                findRouteButton.innerText =
                    "FIND SAFE ROUTE";
            }
        }
    }


    // ============================================================
    // BUTTON EVENTS
    // ============================================================

    findRouteButton.addEventListener(
        "click",
        function () {

            analyzeRoute(false);
        }
    );


    simulationButton.addEventListener(
        "click",
        function () {

            analyzeRoute(true);
        }
    );


    resetSimulationButton.addEventListener(
        "click",
        function () {

            analyzeRoute(false);
        }
    );


    // ============================================================
    // INITIAL LEGEND
    // ============================================================

    addLegend();

});