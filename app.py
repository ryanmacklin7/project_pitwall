import streamlit as st
import altair as alt
from itertools import product
import os
st.set_page_config(
    page_title="Pitwall",
    page_icon="🏎️",
    layout="wide"
)

st.title("🏎️ PITWALL")
st.subheader("F1 Race Strategy Intelligence")

st.write("Build, compare, and optimize your race strategy.")
st.divider()

st.header("Race Configuration")

# 2026 F1 Circuit Calendar
# Format: (race laps, race distance in kilometers)

circuits = {
    "01 - Australia | Albert Park": (58, 306.124),
    "02 - China | Shanghai": (56, 305.066),
    "03 - Japan | Suzuka": (53, 307.471),
    "04 - Miami | Miami International Autodrome": (57, 308.326),
    "05 - Canada | Circuit Gilles Villeneuve": (70, 305.270),
    "06 - Monaco | Circuit de Monaco": (78, 260.286),
    "07 - Barcelona | Circuit de Barcelona-Catalunya": (66, 307.236),
    "08 - Austria | Red Bull Ring": (71, 307.026),
    "09 - Great Britain | Silverstone": (52, 306.198),
    "10 - Belgium | Spa-Francorchamps": (44, 308.052),
    "11 - Hungary | Hungaroring": (70, 306.630),
    "12 - Netherlands | Zandvoort": (72, 306.592),
    "13 - Italy | Monza": (53, 306.720),
    "14 - Spain | Madring": (57, 308.399),
    "15 - Azerbaijan | Baku": (51, 306.049),
    "16 - Bahrain GP | Sepang, Malaysia": (56, 310.417),
    "17 - Singapore | Marina Bay": (62, 305.337),
    "18 - United States | Circuit of the Americas": (56, 308.405),
    "19 - Mexico City | Hermanos Rodriguez": (71, 305.354),
    "20 - Sao Paulo | Interlagos": (71, 305.879),
    "21 - Las Vegas | Las Vegas Strip": (50, 309.958),
    "22 - Qatar | Lusail": (57, 308.611),
    "23 - Abu Dhabi | Yas Marina": (58, 306.188)
}

track_name = st.selectbox(
    "Select Grand Prix Circuit",
    list(circuits.keys())
)

race_laps, race_distance = circuits[track_name]

st.write(f"🏁 Race Laps: {race_laps}")
st.write(f"📏 Race Distance: {race_distance:.3f} km")

st.subheader("Circuit Information")

circuit_name = track_name.split(" | ")[1]

st.write(f"🏎️ {circuit_name}")

circuit_image = f"Circuits/{circuit_name}.png"

if not os.path.exists(circuit_image):
    for filename in os.listdir("Circuits"):
        if filename.lower() == f"{circuit_name}.png".lower():
            circuit_image = os.path.join("Circuits", filename)
            break

if os.path.exists(circuit_image):
    st.image(circuit_image, width=550)
else:
    st.info("Circuit map coming soon.")



number_of_stops = st.selectbox(
    "Pit Stop Strategy",
    [1, 2, 3]
)

st.divider()

st.header("Tire Strategy")

tire_options = ["Soft", "Medium", "Hard"]

selected_tires = []

for stint in range(number_of_stops + 1):
    tire = st.selectbox(
        f"Stint {stint + 1} Tire",
        tire_options,
        index=stint % 3
    )

    selected_tires.append(tire)

st.write("Selected Strategy:", " → ".join(selected_tires))
st.divider()

st.header("Pit Stop Planning")

pit_laps = []

for stop in range(number_of_stops):
    earliest_lap = pit_laps[-1] + 1 if pit_laps else 1
    latest_lap = race_laps - (number_of_stops - stop)

    pit_lap = st.number_input(
        f"Pit Stop {stop + 1} - Lap",
        min_value=earliest_lap,
        max_value=latest_lap,
        value=min(
            max(earliest_lap, race_laps * (stop + 1) // (number_of_stops + 1)),
            latest_lap
        ),
        step=1
    )

    pit_laps.append(pit_lap)

st.write("Planned Pit Laps:", pit_laps)


st.divider()

st.header("Race Simulation")

tires = {
    "Soft": [90.0, 0.12, 18],
    "Medium": [90.7, 0.08, 28],
    "Hard": [91.5, 0.05, 38]
}

pit_loss = 20.5



def calculate_stint_time(stint_length, base_lap_time, degradation, tire_life):
    total_time = 0

    for lap in range(stint_length):
        lap_time = base_lap_time + (degradation * lap)

        if lap >= tire_life:
            laps_over = lap - tire_life + 1
            lap_time += 0.5 * laps_over

        total_time += lap_time

    return total_time


def generate_tire_strategies(number_of_stops):
    compounds = ["Soft", "Medium", "Hard"]
    number_of_stints = number_of_stops + 1

    strategies = []

    for sequence in product(compounds, repeat=number_of_stints):
        if len(set(sequence)) >= 2:
            strategies.append(list(sequence))

    return strategies


def optimize_pit_stops(tire_sequence, race_laps, tires):
    best_time = float("inf")
    best_pit_laps = []

    number_of_stops = len(tire_sequence) - 1

    if number_of_stops == 1:
        for pit_lap in range(1, race_laps):
            predicted_time = calculate_strategy_time(
                tire_sequence,
                [pit_lap],
                race_laps,
                tires
            )

            if predicted_time < best_time:
                best_time = predicted_time
                best_pit_laps = [pit_lap]
    elif number_of_stops == 2:
        for pit1 in range(1, race_laps - 1):
            for pit2 in range(pit1 + 1, race_laps):
                predicted_time = calculate_strategy_time(
                    tire_sequence,
                    [pit1, pit2],
                    race_laps,
                    tires
                )

                if predicted_time < best_time:
                    best_time = predicted_time
                    best_pit_laps = [pit1, pit2]
    
    elif number_of_stops == 3:
        for pit1 in range(1, race_laps - 2, 3):
            for pit2 in range(pit1 + 1, race_laps - 1, 3):
                for pit3 in range(pit2 + 1, race_laps, 3):
                    predicted_time = calculate_strategy_time(
                        tire_sequence,
                        [pit1, pit2, pit3],
                        race_laps,
                        tires
                    )

                    if predicted_time < best_time:
                        best_time = predicted_time
                        best_pit_laps = [pit1, pit2, pit3]


    return best_time, best_pit_laps


def calculate_strategy_time(tire_sequence, pit_laps, race_laps, tires):
    stint_lengths = []
    previous_lap = 0

    for pit_lap in pit_laps:
        stint_lengths.append(pit_lap - previous_lap)
        previous_lap = pit_lap

    stint_lengths.append(race_laps - previous_lap)

    total_time = 0

    for i, tire in enumerate(tire_sequence):
        base_time, degradation, tire_life = tires[tire]

        total_time += calculate_stint_time(
            stint_lengths[i],
            base_time,
            degradation,
            tire_life
        )

    total_time += len(pit_laps) * 20.5

    return total_time

if st.button("🏁 Run Race Simulation", type="primary"):

    tires = {
        "Soft": (90.0, 0.12, 18),
        "Medium": (90.7, 0.08, 28),
        "Hard": (91.5, 0.05, 38)
    }

    stint_lengths = []
    previous_lap = 0

    for pit_lap in pit_laps:
        stint_lengths.append(pit_lap - previous_lap)
        previous_lap = pit_lap

    stint_lengths.append(race_laps - previous_lap)

    total_race_time = 0
    
    stint_results = []

    for i, tire in enumerate(selected_tires):
    
        base_time, degradation, tire_life = tires[tire]

        stint_time = calculate_stint_time(
            stint_lengths[i],
            base_time,
            degradation,
            tire_life
        )

        total_race_time += stint_time

        stint_results.append({
            "Stint": i + 1,
            "Tire": tire,
            "Laps": stint_lengths[i],
            "Stint Time": f"{int(stint_time // 3600)}:{int((stint_time % 3600) // 60):02d}:{stint_time % 60:05.2f}"
        })

        if stint_lengths[i] > tire_life:
            laps_over = stint_lengths[i] - tire_life

            st.warning(
                f"⚠️ STINT {i + 1}: {tire} tire life exceeded! "
                f"Expected life: {tire_life} laps | "
                f"Planned stint: {stint_lengths[i]} laps | "
                f"Over limit: {laps_over} laps"
            )
    total_race_time += number_of_stops * 20.5

    hours = int(total_race_time // 3600)
    minutes = int((total_race_time % 3600) // 60)
    seconds = total_race_time % 60

    st.success("Race Simulation Complete!")

    st.metric(
        "Predicted Race Time",
        f"{hours}:{minutes:02d}:{seconds:05.2f}"
    )

    st.write(f"**Circuit:** {track_name}")
    st.write(f"**Strategy:** {' → '.join(selected_tires)}")
    st.write(f"**Pit Stops:** {pit_laps}")



    st.divider()
    st.subheader("🏎️ Stint Performance")

    st.dataframe(
        stint_results,
        use_container_width=True,
        hide_index=True
    )


    st.divider()
    st.subheader("📈 Tire Degradation Analysis")

    tire_data = {
        "Soft": (90.0, 0.12),
        "Medium": (90.7, 0.08),
        "Hard": (91.5, 0.05)
    }

    chart_data = []

    for tire_name, (base_time, degradation) in tire_data.items():
        for lap in range(1, 31):
            lap_time = base_time + degradation * (lap - 1)

            chart_data.append({
                "Tire Age": lap,
                "Compound": tire_name,
                "Lap Time": round(lap_time, 2)
            })

    import pandas as pd

    df = pd.DataFrame(chart_data)

    chart = alt.Chart(df).mark_line(
        strokeWidth=3
    ).encode(
        x=alt.X("Tire Age:Q", title="Tire Age (Laps)"),
     y=alt.Y(
    "Lap Time:Q",
    title="Lap Time (Seconds)",
    scale=alt.Scale(domain=[89, 100], zero=False)
),
        color=alt.Color(
            "Compound:N",
            scale=alt.Scale(
                domain=["Soft", "Medium", "Hard"],
                range=["#FF3333", "#FFD700", "#FFFFFF"]
            )
        ),
        tooltip=["Compound", "Tire Age", "Lap Time"]
    ).properties(
        height=450
    )

    st.altair_chart(chart, use_container_width=True)


    st.divider()
    st.subheader("🏁 Strategy Comparison")

    comparison_results = []
    
    strategy_options = []

    for tire_sequence in generate_tire_strategies(1):
        strategy_options.append(
            ("1 Stop", tire_sequence, [])
    )
    for tire_sequence in generate_tire_strategies(2):
        strategy_options.append(
            ("2 Stops", tire_sequence, [])
        )

    for tire_sequence in generate_tire_strategies(3):
        strategy_options.append(
            ("3 Stops", tire_sequence, [])
        )

    for strategy_name, tire_sequence, planned_pits in strategy_options:
            if strategy_name in ["1 Stop", "2 Stops", "3 Stops"]:
                predicted_time, planned_pits = optimize_pit_stops(
                    tire_sequence,
                    race_laps,
                    tires
                )
            else:
                predicted_time = calculate_strategy_time(
                    tire_sequence,
                    planned_pits,
                    race_laps,
                    tires
                )

            comparison_results.append({
                "Strategy": strategy_name,
                "Tires": " → ".join(tire_sequence),
                "Pit Laps": ", ".join(str(lap) for lap in planned_pits),
                "Predicted Race Time": f"{int(predicted_time // 3600)}:{int((predicted_time % 3600) // 60):02d}:{predicted_time % 60:05.2f}"
            })
    # Include the driver's selected strategy
    comparison_results.append({
        "Strategy": "Your Strategy",
        "Tires": " → ".join(selected_tires),
        "Pit Laps": ", ".join(str(lap) for lap in pit_laps),
        "Predicted Race Time": (
            f"{int(total_race_time // 3600)}:"
            f"{int(total_race_time % 3600 // 60):02d}:"
            f"{total_race_time % 60:05.2f}"
        )
    })

    comparison_results.sort(
        key=lambda strategy: calculate_strategy_time(
            strategy["Tires"].split(" → "),
            [int(lap.strip()) for lap in strategy["Pit Laps"].split(",") if lap.strip()],
            race_laps,
            tires
        )
    )
    st.dataframe(
        comparison_results,
        use_container_width=True,
        hide_index=True
    ) 



    # Find the fastest strategy
    best_strategy = min(
        comparison_results,
        key=lambda strategy: calculate_strategy_time(
            strategy["Tires"].split(" → "),
            [int(lap.strip()) for lap in strategy["Pit Laps"].split(",")],
            race_laps,
            tires
        )
    )

    st.divider()
    st.subheader("🏆 PITWALL Recommended Strategy")

    st.success(f"Recommended: {best_strategy['Strategy']}")

    st.write(f"**Tire Strategy:** {best_strategy['Tires']}")
    st.write(f"**Pit Stop Laps:** {best_strategy['Pit Laps']}")
    st.metric(
        "Predicted Race Time",
        best_strategy["Predicted Race Time"]
    )
    # Compare driver's strategy with Pitwall recommendation
    best_time = calculate_strategy_time(
        best_strategy["Tires"].split(" → "),
        [int(lap.strip()) for lap in best_strategy["Pit Laps"].split(",")],
        race_laps,
        tires
    )

    time_saved = total_race_time - best_time

    st.divider()
    st.subheader("🏎️ Race Engineer Analysis")

    if time_saved > 0.01:
        minutes_saved = int(time_saved // 60)
        seconds_saved = time_saved % 60

        st.success(
            f"💡 Pitwall can save you "
            f"{minutes_saved}m {seconds_saved:.2f}s "
            f"with the recommended strategy!"
        )

    elif time_saved < -0.01:
        st.info(
            "🏆 Your selected strategy is faster than "
            "the strategies Pitwall compared!"
        )

    else:
        st.success(
            "🏆 Excellent strategy! Your selected strategy "
            "matches Pitwall's fastest prediction!"
        )
