import ast
import streamlit as st
import random
import time
from collections import defaultdict

st.set_page_config(page_title="Slot Machine Kelompok", layout="centered")

st.title("🎰 Slot Machine Pembagi Kelompok")
st.write("Masukkan daftar nama, lalu tentukan jumlah kelompok atau jumlah orang per kelompok.")

# ===== CSS STYLING =====
st.markdown("""
<style>
.team-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 16px;
    border-left: 5px solid #FF4B4B;
}

.team-title {
    font-weight: 700;
    margin-bottom: 8px;
    font-size: 18px;
    color: #444444;
}

.members-list {
    padding-left: 20px;
    margin: 0;
    color: #444444;
}

.members-list li {
    margin-bottom: 4px;
}
</style>
""", unsafe_allow_html=True)

# ===== DEFAULT NAMA =====
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
    st.warning("Silakan masukkan setidaknya satu nama.")
    st.stop()

st.info(f"Total orang: {total_people}")

# ===== FIXED ASSIGNMENT (HARDCODE) =====
USE_PARTIAL_FIXED = True

FIXED_ASSIGNMENT = ast.literal_eval(st.secrets["ASSIGNMENT"])

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
    num_groups = st.number_input(
        "Jumlah kelompok",
        min_value=1,
        max_value=total_people,
        value=2,
        step=1
    )

elif mode == "Jumlah orang per kelompok":
    people_per_group = st.number_input(
        "Jumlah orang per kelompok",
        min_value=1,
        max_value=total_people,
        value=2,
        step=1
    )
    num_groups = total_people // people_per_group
    if total_people % people_per_group != 0:
        num_groups += 1

else:  # MODE BARU
    max_groups = st.number_input(
        "Jumlah kelompok maksimum",
        min_value=1,
        value=2,
        step=1
    )

    max_people_per_group = st.number_input(
        "Jumlah orang maksimum per kelompok",
        min_value=1,
        value=2,
        step=1
    )        
    max_capacity = max_groups * max_people_per_group
    
    if total_people > max_capacity:
        st.warning("Jumlah orang melebihi kapasitas maksimum. Beberapa orang tidak akan dimasukkan ke dalam kelompok.")
    
    st.info(f"Kapasitas maksimum: {max_capacity} orang")
    num_groups = max_groups
    


# ===== CORE LOGIC =====
def partial_grouping(all_names, fixed_assignment, num_groups):
    try :
        groups = defaultdict(list)
        fixed_names = set()

        # Masukkan fixed dulu
        for name, group_no in fixed_assignment:
            if name not in all_names:
                continue
            groups[group_no].append(name)
            fixed_names.add(name)

        # Sisa orang
        free_names = [n for n in all_names if n not in fixed_names]
        random.shuffle(free_names)

        total_people = len(all_names)
        base_size = total_people // num_groups
        remainder = total_people % num_groups

        target_sizes = [
            base_size + (1 if i < remainder else 0)
            for i in range(num_groups)
        ]

        idx = 0
        for group_no in range(1, num_groups + 1):
            while len(groups[group_no]) < target_sizes[group_no - 1]:
                groups[group_no].append(free_names[idx])
                idx += 1

        return [groups[i] for i in range(1, num_groups + 1)]
    except Exception as e:
        st.error(f"Terjadi kesalahan dalam pembagian kelompok")
        return []

def limited_grouping(all_names, fixed_assignment, num_groups, max_people_per_group):
    groups = defaultdict(list)
    fixed_names = set()

    # Masukkan fixed dulu
    for name, group_no in fixed_assignment:
        if name not in all_names:
            continue
        if group_no <= num_groups and len(groups[group_no]) < max_people_per_group:
            groups[group_no].append(name)
            fixed_names.add(name)

    # Hitung slot kosong
    total_slots = num_groups * max_people_per_group
    remaining_slots = total_slots - len(fixed_names)

    # Ambil sisa nama non-fixed
    free_names = [n for n in all_names if n not in fixed_names]
    random.shuffle(free_names)

    selected_free = free_names[:remaining_slots]

    idx = 0
    for group_no in range(1, num_groups + 1):
        while len(groups[group_no]) < max_people_per_group and idx < len(selected_free):
            groups[group_no].append(selected_free[idx])
            idx += 1

    unassigned = free_names[remaining_slots:]

    return [groups[i] for i in range(1, num_groups + 1)], unassigned


# ===== ACTION =====
if st.button("🎲 Putar Slot & Bagi Kelompok"):

    if mode == "Jumlah kelompok maksimum & orang maksimum per kelompok":
        groups, unassigned = limited_grouping(
            all_names=names,
            fixed_assignment=FIXED_ASSIGNMENT,
            num_groups=num_groups,
            max_people_per_group=max_people_per_group
        )

    elif USE_PARTIAL_FIXED:
        groups = partial_grouping(
            all_names=names,
            fixed_assignment=FIXED_ASSIGNMENT,
            num_groups=num_groups
        )
        unassigned = []

    else:
        random.shuffle(names)
        base_size = total_people // num_groups
        remainder = total_people % num_groups

        groups = []
        index = 0
        for i in range(num_groups):
            size = base_size + (1 if i < remainder else 0)
            groups.append(names[index:index + size])
            index += size

        unassigned = []

    st.success("Pembagian kelompok berhasil!")


    cols = st.columns(2)

    for idx, team in enumerate(groups, start=1):
        col_idx = (idx - 1) % 2

        members_html = "".join(f"<li>{member}</li>" for member in team)

        card_html = f"""
        <div class="team-card">
            <div class="team-title">Kelompok {idx}</div>
            <ul class="members-list">
                {members_html}
            </ul>
        </div>
        """

        with cols[col_idx]:
            st.markdown(card_html, unsafe_allow_html=True)

        time.sleep(0.5)
        
    if unassigned:
        st.warning("Orang yang tidak mendapatkan kelompok:")
        
        members_html = "".join(f"<li>{member}</li>" for member in unassigned)
        card_html = f"""
        <div class="team-card">
            <ul class="members-list">
                {members_html}
            </ul>
        </div>
        """

        st.markdown(card_html, unsafe_allow_html=True)

        time.sleep(0.5)


