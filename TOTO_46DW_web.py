import streamlit as st
import pandas as pd

# --- DEINE ORIGINAL-MATRIX ---
A, B, C = "111222XXX", "222XXX111", "XXX111222"
P1, P2, P3 = "12X12X12X", "2X12X12X1", "X12X12X12"
Q = "12X2X1X12"

BLOECKE_STRUKTUR = [
    (A, P1, P2, Q), (B, P1, P2, Q), (C, P1, P2, Q),
    (B, P2, P3, Q), (C, P2, P3, Q), (A, P2, P3, Q),
    (C, P3, P1, Q), (A, P3, P1, Q), (B, P3, P1, Q)
]

# --- WEB-OBERFLÄCHE ---
st.set_page_config(page_title="MAI Toto-Mobile", layout="centered")
st.title("⚽ MAI Toto-Designer")

st.markdown("### 1. Spiele-Konfiguration")
st.info("Wähle Typ und Favorit. Favorit '-' zählt nicht in die Statistik.")

alle_wahl = []
alle_favs = []

for i in range(6):
    with st.container():
        st.markdown(f"**Spiel {i+1}**")
        col_typ, col_fav = st.columns([2, 1])
        with col_typ:
            wahl = st.selectbox(f"Typ S{i+1}", ["DW", "1", "X", "2", "-"], index=0 if i < 4 else 4, key=f"w{i}", label_visibility="collapsed")
        with col_fav:
            if wahl == "DW":
                fav = st.selectbox(f"Favorit S{i+1}", ["-", "1", "X", "2"], index=0, key=f"f{i}", label_visibility="collapsed")
            elif wahl == "-":
                fav = "-"
                st.text("---")
            else:
                fav = wahl
                st.text(f"Bank {wahl}")
        alle_wahl.append(wahl)
        alle_favs.append(fav)
    st.divider()

st.markdown("### 2. Filter")
anz_fav = st.number_input("Anzahl Favorit (Ziel):", min_value=0, max_value=6, value=2)
untergrenze = max(0, anz_fav - 2)

# --- LOGIK ---
dw_indices = [i for i, x in enumerate(alle_wahl) if x == "DW"]
banken = {i: x for i, x in enumerate(alle_wahl) if x in ["1", "X", "2"]}
aktive_spiele = [i for i, x in enumerate(alle_wahl) if x != "-"]

if len(dw_indices) >= 4:
    n_dw = len(dw_indices)
    anz_bloecke = 1 if n_dw == 4 else (3 if n_dw == 5 else 9)
    ergebnis = []

    for b_idx in range(anz_bloecke):
        s1, s2, s3, s4 = BLOECKE_STRUKTUR[b_idx]
        char5 = ["1", "2", "X"][b_idx % 3]
        char6 = ["1", "2", "X"][b_idx // 3]

        for t_idx in range(9):
            tipp_dw = [s1[t_idx], s2[t_idx], s3[t_idx], s4[t_idx]]
            if n_dw >= 5: tipp_dw.append(char5)
            if n_dw >= 6: tipp_dw.append(char6)
            
            k_tipp = ["-"] * 6
            for idx, pos in enumerate(dw_indices): k_tipp[pos] = tipp_dw[idx]
            for pos, wert in banken.items(): k_tipp[pos] = wert
            
            # Trefferzählung
            tr_dw = 0
            for idx, pos in enumerate(dw_indices):
                if alle_favs[pos] != "-" and tipp_dw[idx] == alle_favs[pos]:
                    tr_dw += 1
            
            if tr_dw >= untergrenze:
                tipp_string = " ".join([k_tipp[j] for j in aktive_spiele])
                status = "Kern-Tipp" if tr_dw == anz_fav else "Absicherung"
                ergebnis.append({"Tipp": tipp_string, "Treffer": tr_dw, "Kategorie": status})

    # --- ANZEIGE ---
    st.divider()
    st.subheader(f"Ergebnis: {len(ergebnis)} Tipps")

    if ergebnis:
        df = pd.DataFrame(ergebnis)
        df.index = range(1, len(df) + 1)
        
        # Styling ohne Warnzeichen
        def color_status(val):
            if val == "Kern-Tipp":
                return 'background-color: #d4edda; color: #155724; font-weight: bold'
            return 'background-color: #d1ecf1; color: #0c5460'

        st.table(df.style.applymap(color_status, subset=['Kategorie']))
        
        csv = df.to_csv(index=True).encode('utf-8')
        st.download_button("Liste speichern", csv, "toto_tipps.csv", "text/csv")
else:
    st.warning("Bitte mindestens 4 Dreiwege (DW) einstellen.")
