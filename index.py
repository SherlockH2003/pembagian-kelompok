import ast
import streamlit as st
import random
import time

st.set_page_config(page_title="Slot Machine Kelompok", layout="centered")

st.title("🎰 Slot Machine Pembagi Kelompok")
st.write("Masukkan daftar nama, lalu tentukan metode pembagian kelompok.")

# ===== CSS =====
st.markdown("""
<style>
.team-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 16px;
    border-left: 5px solid #FF4B4B;
    color: #333;
}
.team-title {
    font-weight: 700;
    margin-bottom: 8px;
    font-size: 18px;
    color: #444;
}
.members-list {
    padding-left: 20px;
    margin: 0;
}
.members-list li {
    margin-bottom: 4px;
}
</style>
""", unsafe_allow_html=True)

# ===== INPUT =====
default_names = """Nama 1
Nama 2
Nama 3
Nama 4
Nama 5
Nama 6
Nama 7
Nama 8"""

names_input = st.text_area(
    "Masukkan nama (1 nama per baris)",
    value=default_names,
    height=220
)

names = [n.strip() for n in names_input.split("\n") if n.strip()]
total_people = len(names)

if total_people == 0:
    st.warning("Masukkan minimal satu nama.")
    st.stop()

st.info(f"Total orang: {total_people}")

# ===== FIXED CLUSTER =====
USE_FIXED_CLUSTER = True
FIXED_CLUSTERS = ast.literal_eval(st.secrets["ASSIGNMENT"])

# ===== MODE =====
mode = st.radio(
    "Pilih metode pembagian:",
    [
        "Jumlah kelompok",
        "Jumlah orang per kelompok",
        "Jumlah kelompok maksimum & orang maksimum per kelompok"
    ]
)

if mode == "Jumlah kelompok":
    num_groups = st.number_input("Jumlah kelompok", 1, total_people, 2)
    max_people_per_group = None

elif mode == "Jumlah orang per kelompok":
    people_per_group = st.number_input("Jumlah orang per kelompok", 1, total_people, 2)
    num_groups = total_people // people_per_group
    if total_people % people_per_group != 0:
        num_groups -= 1
    max_people_per_group = people_per_group

else:
    num_groups = st.number_input("Jumlah kelompok maksimum", 1, total_people, 2)
    max_people_per_group = st.number_input("Jumlah orang maksimum per kelompok", 1, total_people, 2)

# ===== CORE LOGIC (FIX TOTAL FIX) =====
def safe_cluster_grouping(all_names, clusters, num_groups, max_per_group):

    groups = [[] for _ in range(num_groups)]

    # valid cluster
    clusters = [
        [n for n in c if n in all_names]
        for c in clusters
        if len(c) > 0
    ]

    random.shuffle(clusters)
    used = set()

    # 1️⃣ cluster ke grup berbeda
    available_indexes = list(range(num_groups))
    random.shuffle(available_indexes)

    for c in clusters:
        idx = available_indexes.pop()
        groups[idx].extend(c)
        used.update(c)


    # 2️⃣ sisa orang
    free_names = [n for n in all_names if n not in used]
    random.shuffle(free_names)

    total = len(all_names)

    # ukuran ideal
    base = total // num_groups
    extra = total % num_groups

    target_sizes = []
    for i in range(num_groups):
        size = base + (1 if i < extra else 0)
        if max_per_group:
            size = max(size, max_per_group)
        target_sizes.append(size)

    # 3️⃣ isi grup sampai target
    idx = 0
    for name in free_names:
        while len(groups[idx]) >= target_sizes[idx]:
            idx = (idx + 1) % num_groups
        groups[idx].append(name)

    # 4️⃣ shuffle internal
    for g in groups:
        random.shuffle(g)

    return groups, []

# ===== ACTION =====
if st.button("🎲 Putar Slot & Bagi Kelompok"):

    groups, _ = safe_cluster_grouping(
        names,
        FIXED_CLUSTERS if USE_FIXED_CLUSTER else [],
        num_groups,
        max_people_per_group
    )

    st.success("Pembagian kelompok berhasil!")

    cols = st.columns(2)
    for idx, team in enumerate(groups, start=1):
        members_html = "".join(f"<li>{m}</li>" for m in team)
        card = f"""
        <div class="team-card">
            <div class="team-title">Kelompok {idx}</div>
            <ul class="members-list">{members_html}</ul>
        </div>
        """
        with cols[(idx - 1) % 2]:
            st.markdown(card, unsafe_allow_html=True)
        time.sleep(0.2)

