import re
import tkinter as tk
from tkinter import ttk

# ---------- Aturan perpustakaan (mudah diubah) ----------
BATAS_PINJAM = 7       
BATAS_TERLAMBAT = 30   
DENDA_PER_HARI = 1000  
JUMLAH_MAKS = 5
PANJANG_NOMOR = 6

# ===================== LOGIKA (hasil perbaikan / FIX) =====================
def rapikan(t):
    """buang spasi di tepi dan spasi ganda"""
    return " ".join(t.split())


def rupiah(n):
    return "Rp" + f"{n:,}".replace(",", ".")


def angka_saja(t):
    return re.fullmatch(r"[0-9]+", t) is not None


def validasi_nomor(teks):
    """kembalikan pesan error, atau '' jika valid"""
    teks = rapikan(teks)
    if not angka_saja(teks):
        return "Nomor anggota harus berupa angka."
    return f"Nomor anggota harus {PANJANG_NOMOR} digit." if len(teks) != PANJANG_NOMOR else ""


def validasi_angka(teks, nama, minimum, maksimum=None):
    teks = rapikan(teks)
    if teks.startswith("-") and angka_saja(teks[1:]):
        return nama + " tidak boleh minus."
    if not angka_saja(teks):
        return nama + " harus berupa angka bulat."
    if len(teks) > 1 and teks.startswith("0"):
        return "Tidak boleh diawali angka 0."
    angka = int(teks)
    if angka < minimum:
        return f"{nama} minimal {minimum}."
    if maksimum is not None and angka > maksimum:
        return f"{nama} maksimal {maksimum}."
    return ""


# ===================== SIMULASI: versi BUG dan FIX =====================
# 1. Nomor anggota
def nomor_bug(t):
    return f"Nomor {t} diterima" if len(t) == 6 else "Error: nomor tidak valid"


def nomor_fix(t):
    p = validasi_nomor(t)
    return "Error: " + p if p else f"Nomor {rapikan(t)} diterima"


# 2. Denda peminjaman
def lama_bug(t):
    terlambat = int(t) - 7
    return f"Terlambat {terlambat} hari, denda {rupiah(terlambat * 1000)}"


def lama_fix(t):
    p = validasi_angka(t, "Lama pinjam", 1)
    if p:
        return "Error: " + p
    lama = int(rapikan(t))
    terlambat = max(0, lama - BATAS_PINJAM)   # terlambat mulai hari ke-8
    hasil = f"Terlambat {terlambat} hari, denda {rupiah(terlambat * DENDA_PER_HARI)}"
    if terlambat > BATAS_TERLAMBAT:
        hasil += f"\nPERHATIAN: terlambat melewati {BATAS_TERLAMBAT} hari. Anda tidak boleh meminjam lagi."   # denda tetap dihitung
    return hasil


# 3. Jumlah buku
def jumlah_bug(t):
    return f"{int(t)} buku dipinjam" if int(t) > 0 else "Error: jumlah tidak valid"


def jumlah_fix(t):
    p = validasi_angka(t, "Jumlah buku", 1, JUMLAH_MAKS)
    return "Error: " + p if p else f"{int(rapikan(t))} buku dipinjam"


# nama: (fungsi bug, fungsi fix, aturan, kode bug, kode fix)
SKENARIO = {
    "Nomor anggota": (
        nomor_bug, nomor_fix,
        "Aturan: nomor anggota harus tepat 6 digit angka.",
        "def nomor_bug(teks):\n    # hanya cek panjang\n    if len(teks) == 6:\n        return 'diterima'\n    return 'Error'",
        "def nomor_fix(teks):\n    pesan = validasi_nomor(teks)\n    if pesan:\n        return 'Error: ' + pesan\n    return 'diterima'"),
    "Denda peminjaman": (
        lama_bug, lama_fix,
        "Aturan: boleh pinjam 7 hari tanpa denda, lewat dari itu denda Rp1.000 per hari. Terlambat maksimal 30 hari (lama pinjam 37 hari). Terlambat hari ke-31 (lama pinjam 38 hari) dst muncul pemberitahuan tidak boleh pinjam lagi.",
        "def lama_bug(teks):\n    lama = int(teks)   # crash jika bukan angka\n    terlambat = lama - 7   # bisa minus\n    return terlambat * 1000",
        "def lama_fix(teks):\n    pesan = validasi_angka(\n        teks, 'Lama pinjam', 1)\n    if pesan:\n        return 'Error: ' + pesan\n    lama = int(teks)\n    terlambat = max(0, lama - 7)\n    hasil = terlambat * 1000\n    if terlambat > 30:   # denda tetap\n        hasil += ' + dilarang pinjam'\n    return hasil"),
    "Jumlah buku": (
        jumlah_bug, jumlah_fix,
        "Aturan: jumlah buku 1 sampai 5 per transaksi.",
        "def jumlah_bug(teks):\n    jumlah = int(teks)\n    if jumlah > 0:   # tanpa batas atas\n        return 'diterima'",
        "def jumlah_fix(teks):\n    pesan = validasi_angka(\n        teks, 'Jumlah buku', 1, 5)\n    if pesan:\n        return 'Error: ' + pesan\n    return 'diterima'"),
}

# fitur: (masalah di BUG, perbaikan di FIX, alasan)
TABEL = {
    "Nomor anggota": (
        "Hanya mengecek panjang 6 karakter, jadi “12ab56” dan “@@@@@@” ikut lolos.",
        "Dicek dulu apakah semuanya angka, baru dicek panjangnya harus 6 digit.",
        "Nomor anggota itu kode angka. Kalau ada huruf atau simbol, data jadi kacau dan anggota susah dicari."),
    "Denda peminjaman": (
        "Tidak dicek. Angka minus menghasilkan hari terlambat dan denda minus, huruf membuat program error, dan 66 hari tetap diterima.",
        "Harus angka bulat minimal 1. Boleh 7 hari tanpa denda, hari ke-8 dst dihitung terlambat, denda Rp1.000 per hari. Terlambat maksimal 30 hari; terlambat hari ke-31 dst muncul pemberitahuan tidak boleh pinjam lagi, dendanya tetap dihitung.",
        "Lama pinjam tidak mungkin minus atau nol, dan program tidak boleh mati hanya karena salah ketik. Ada batas maksimal keterlambatan 30 hari supaya buku tidak ditahan terlalu lama."),
    "Jumlah buku": (
        "Hanya mengecek lebih dari 0, jadi pinjam 9 atau 100 buku tetap diterima.",
        "Jumlah harus angka bulat 1 sampai 5 per transaksi.",
        "Ada batas pinjam per transaksi. Tanpa batas, satu orang bisa meminjam terlalu banyak dan buku cepat habis."),
}

# ===================== TAMPILAN (GUI Tkinter) =====================
BG = "#F4F0FA"
HEAD = "#563D70"
RULE_BG = "#E8F0FA"
RULE_INK = "#1F3A5F"
WARNA = {"bug": "#C0392B", "fix": "#2E7D5B", "abu": "#777777"}
TH = "#D81B7A"

root = tk.Tk()
root.title("Simulasi BUG & FIX - Denda Perpustakaan")
root.geometry("960x860")
root.minsize(760, 700)
root.configure(bg=BG)

# area scroll agar muat di layar kecil
canvas = tk.Canvas(root, bg=BG, highlightthickness=0)
sb = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=sb.set)
sb.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)
main = tk.Frame(canvas, bg=BG, padx=25, pady=12)
win = canvas.create_window((0, 0), window=main, anchor="nw")
main.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.bind("<Configure>", lambda e: canvas.itemconfigure(win, width=e.width))
canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-e.delta / 120) or (-1 if e.delta > 0 else 1), "units"))

tk.Label(main, text="SIMULASI BUG & FIX", font=("Arial", 22, "bold"), fg=HEAD, bg=BG).pack()
tk.Label(main, text="Denda Perpustakaan", font=("Arial", 12), fg=HEAD, bg=BG).pack()
tk.Label(main, text="Kelompok 7", font=("Arial", 12, "bold"), fg=HEAD, bg=BG).pack()

tk.Label(main, text="1. Coba Program", font=("Arial", 13, "bold"), fg=HEAD, bg=BG, anchor="w").pack(fill="x", pady=(16, 4))
pilih = ttk.Combobox(main, values=list(SKENARIO.keys()), state="readonly", font=("Arial", 11))
pilih.pack(fill="x")
pilih.current(0)

lbl_aturan = tk.Label(main, bg=RULE_BG, fg=RULE_INK, font=("Arial", 11), anchor="w", justify="left", padx=10, pady=8)
lbl_aturan.pack(fill="x", pady=8)

tk.Label(main, text="Masukkan nilai uji:", font=("Arial", 11), bg=BG, anchor="w").pack(fill="x")
entry = tk.Entry(main, font=("Arial", 14))
entry.pack(fill="x", pady=(2, 0), ipady=4)

frm_btn = tk.Frame(main, bg=BG)
frm_btn.pack(pady=12)


def tombol(teks, warna, cmd):
    b = tk.Button(frm_btn, text=teks, bg=warna, fg="white", activebackground=warna, activeforeground="white",
                  font=("Arial", 11, "bold"), relief="flat", padx=18, pady=6, cursor="hand2", command=cmd)
    b.pack(side="left", padx=5)
    return b


frm_dua = tk.Frame(main, bg=BG)
frm_dua.pack(fill="x")
frm_dua.columnconfigure((0, 1), weight=1, uniform="a")


def kotak_hasil(kolom, judul):
    f = tk.Frame(frm_dua, bg=BG)
    f.grid(row=0, column=kolom, sticky="nsew", padx=4)
    tk.Label(f, text=judul, font=("Arial", 10, "bold"), bg=BG, anchor="w").pack(fill="x")
    l = tk.Label(f, text="", bg="white", font=("Arial", 11, "bold"), anchor="nw", justify="left",
                 relief="solid", bd=1, padx=10, pady=8, height=5, wraplength=380)
    l.pack(fill="both", expand=True)
    return l


h_bug = kotak_hasil(0, "X Sebelum / BUG")
h_fix = kotak_hasil(1, "V Sesudah / FIX")

tk.Label(main, text="2. Perhatikan Kode", font=("Arial", 13, "bold"), fg=HEAD, bg=BG, anchor="w").pack(fill="x", pady=(18, 4))
frm_kode = tk.Frame(main, bg=BG)
frm_kode.pack(fill="x")
frm_kode.columnconfigure((0, 1), weight=1, uniform="b")


def kotak_kode(kolom):
    t = tk.Text(frm_kode, height=11, width=10, bg="#1E1E2E", fg="white", insertbackground="white",
                font=("Consolas", 10), relief="flat", padx=10, pady=10, wrap="none")
    t.grid(row=0, column=kolom, sticky="nsew", padx=4)
    return t


k_bug = kotak_kode(0)
k_fix = kotak_kode(1)

tk.Label(main, text="3. Penjelasan Fitur", font=("Arial", 13, "bold"), fg=HEAD, bg=BG, anchor="w").pack(fill="x", pady=(18, 4))
frm_tabel = tk.Frame(main, bg="#999999", padx=1, pady=1)
frm_tabel.pack(fill="x")
for i, w in enumerate((1, 3, 3, 3)):
    frm_tabel.columnconfigure(i, weight=w, uniform="t")
for i, judul in enumerate(("Fitur", "Masalah di versi BUG", "Perbaikan di versi FIX", "Alasan")):
    tk.Label(frm_tabel, text=judul, bg=TH, fg="white", font=("Arial", 10, "bold"), anchor="w",
             padx=6, pady=6).grid(row=0, column=i, sticky="nsew", padx=(0, 1), pady=(0, 1))
sel = []
for i in range(4):
    l = tk.Label(frm_tabel, text="", bg="white", font=("Arial", 10, "bold" if i == 0 else "normal"),
                 anchor="nw", justify="left", padx=6, pady=6, wraplength=150)
    l.grid(row=1, column=i, sticky="nsew", padx=(0, 1))
    sel.append(l)


def atur_wrap(_=None):
    lebar = frm_dua.winfo_width()
    for l in (h_bug, h_fix):
        l.configure(wraplength=max(150, lebar // 2 - 30))
    lbl_aturan.configure(wraplength=max(200, main.winfo_width() - 70))
    total = frm_tabel.winfo_width()
    unit = max(40, total // 10)
    sel[0].configure(wraplength=unit - 14)
    for l in sel[1:]:
        l.configure(wraplength=unit * 3 - 14)


main.bind("<Configure>", lambda e: (canvas.configure(scrollregion=canvas.bbox("all")), atur_wrap()))


def tampil(el, teks, w):
    el.configure(text=teks, fg=w)


def isi_kode(widget, teks):
    widget.configure(state="normal")
    widget.delete("1.0", "end")
    widget.insert("1.0", teks)
    widget.configure(state="disabled")


def jalankan(mode):
    f_bug, f_fix = SKENARIO[pilih.get()][:2]
    fungsi = f_bug if mode == "bug" else f_fix
    try:
        hasil = fungsi(entry.get())
    except Exception as e:
        hasil = "CRASH: " + (type(e).__name__ or "Error")
    if mode == "bug":
        tampil(h_bug, hasil, WARNA["bug"])
    else:
        tampil(h_fix, hasil, WARNA["fix"])


def reset_simulasi(_=None):
    fitur = pilih.get()
    _, _, aturan, kode_bug, kode_fix = SKENARIO[fitur]
    lbl_aturan.configure(text=aturan)
    entry.delete(0, "end")
    tampil(h_bug, "(klik Jalankan BUG)", WARNA["abu"])
    tampil(h_fix, "(klik Jalankan FIX)", WARNA["abu"])
    isi_kode(k_bug, kode_bug)
    isi_kode(k_fix, kode_fix)
    for l, t in zip(sel, (fitur, *TABEL[fitur])):
        l.configure(text=t)
    entry.focus_set()


tombol("X Jalankan BUG", WARNA["bug"], lambda: jalankan("bug"))
tombol("V Jalankan FIX", WARNA["fix"], lambda: jalankan("fix"))
tombol("Reset", "#5A6B8C", reset_simulasi)

pilih.bind("<<ComboboxSelected>>", reset_simulasi)
entry.bind("<Return>", lambda e: jalankan("fix"))

reset_simulasi()
root.after(100, atur_wrap)
root.mainloop()
