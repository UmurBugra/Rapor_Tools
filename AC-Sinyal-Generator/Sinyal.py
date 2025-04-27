import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, TextBox, RadioButtons
import matplotlib.gridspec as gridspec

# Ana figür oluşturma
plt.style.use('dark_background')
fig = plt.figure(figsize=(12, 8))
gs = gridspec.GridSpec(2, 1, height_ratios=[4, 1])

# Osiloskop ekranı için alt figür
ax_scope = plt.subplot(gs[0])
ax_controls = plt.subplot(gs[1])

# Başlangıç değerleri
initial_vpp = 10.0  # V
initial_freq = 1000  # Hz
initial_volt_div = 2.0  # V/div
initial_time_div = 0.1  # ms/div

# Şu anki değerler (global olarak tanımla)
global vpp_val, freq_val, volt_div_val, time_div_val, signal_type_val, duty_cycle_val, symmetry_val
vpp_val = initial_vpp
freq_val = initial_freq
volt_div_val = initial_volt_div
time_div_val = initial_time_div
signal_type_val = 'sine'  # Varsayılan sinyal tipi
duty_cycle_val = 50  # Varsayılan duty cycle
symmetry_val = 50  # Varsayılan symmetry


# Zaman ve sinyal değerlerini hesaplama
def calculate_signal(vpp, freq, time_div, signal_type='sine', duty_cycle=50, symmetry=50):
    amplitude = vpp / 2
    period = 1 / freq  # saniye cinsinden
    # Ekranda 15 time division olduğunu varsayalım (daha fazla periyot görmek için)
    time_range = 15 * time_div / 1000  # ms -> s
    t = np.linspace(0, time_range, 1500)

    if signal_type == 'sine':
        # Sinüs dalgası
        y = amplitude * np.sin(2 * np.pi * freq * t)
    elif signal_type == 'square':
        # Kare dalga
        # Duty cycle: Sinyalin yüksek durumda kalma oranı (%)
        y = amplitude * np.sign(np.sin(2 * np.pi * freq * t - np.pi * (duty_cycle / 50 - 1)))
    elif signal_type == 'triangle':
        # Üçgen dalga
        # Symmetry: Üçgen dalganın yükselme ve düşme sürelerinin oranı (%)
        # 50% olduğunda, simetrik üçgen (eşit yükselme/düşme süresi)
        # 50%'den az olduğunda, yükselme süresi daha kısa
        # 50%'den fazla olduğunda, düşme süresi daha kısa
        symmetry_norm = symmetry / 100.0  # 0-1 aralığına normalize et

        # Modifiye edilmiş testere dişi dalgası oluşturalım
        sawtooth = 2 * (freq * t - np.floor(freq * t + symmetry_norm))

        # Symmetry'ye göre şekillendirme
        y = amplitude * np.where(sawtooth >= 0,
                                 1 - sawtooth / symmetry_norm if symmetry_norm > 0 else 0,
                                 1 + sawtooth / (1 - symmetry_norm) if symmetry_norm < 1 else 0)

    return t, y


t, y = calculate_signal(initial_vpp, initial_freq, initial_time_div)

# Osiloskop ekranını çizme
line, = ax_scope.plot(t, y, 'y-', linewidth=2)


# Izgara ayarları
def setup_grid(volt_div, time_div):
    global vpp_val, freq_val

    # Eksen sınırlarını ayarla
    ax_scope.set_xlim(0, 15 * time_div / 1000)
    ax_scope.set_ylim(-5 * volt_div, 5 * volt_div)

    # X ekseni ızgarası (zaman)
    time_ticks = np.linspace(0, 15 * time_div / 1000, 16)
    ax_scope.set_xticks(time_ticks)
    ax_scope.set_xticklabels([f"{i * time_div:.1f}" for i in range(16)])

    # Y ekseni ızgarası (voltaj)
    volt_ticks = np.linspace(-5 * volt_div, 5 * volt_div, 11)
    ax_scope.set_yticks(volt_ticks)
    ax_scope.set_yticklabels([f"{v:.1f}" for v in volt_ticks])

    # Izgara çizgileri
    ax_scope.grid(True, color='green', linestyle='-', linewidth=0.5, alpha=0.5)

    # Eksen etiketleri
    time_unit = "ms"
    time_val = time_div

    # 1 ms'den küçük değerler için µs (mikrosaniye) göster
    if time_div < 1.0:
        time_unit = "μs"
        time_val = time_div * 1000

    ax_scope.set_xlabel(f'Zaman ({time_unit}) - {time_val:.0f} {time_unit}/div', color='white')
    ax_scope.set_ylabel(f'Voltaj (V) - {volt_div} V/div', color='white')

    # Ekran başlığı - İlk çağrıda başlangıç değerlerini kullan
    current_vpp = vpp_val if 'vpp_val' in globals() else initial_vpp
    current_freq = freq_val if 'freq_val' in globals() else initial_freq

    ax_scope.set_title(f'Osiloskop Simülatörü - {current_vpp:.1f} Vpp, {current_freq:.0f} Hz', color='white')


# Bilgi metnini güncelleme fonksiyonu
def update_info_text():
    # Time/Div için birim ayarlama
    time_unit = "ms"
    time_val = time_div_val

    # 1 ms'den küçük değerler için µs (mikrosaniye) göster
    if time_div_val < 1.0:
        time_unit = "μs"
        time_val = time_div_val * 1000

    # Sinyal tipi bilgisini ekle
    signal_info = ""
    if signal_type_val == 'sine':
        signal_info = "Sinüs"
    elif signal_type_val == 'square':
        signal_info = f"Kare (Duty: {duty_cycle_val:.0f}%)"
    elif signal_type_val == 'triangle':
        signal_info = f"Üçgen (Sym: {symmetry_val:.0f}%)"

    info_text = f"""
    Sinyal: {signal_info}
    Vpp: {vpp_val:.1f} V
    Frekans: {freq_val:.0f} Hz
    Volt/Div: {volt_div_val:.1f} V
    Time/Div: {time_val:.0f} {time_unit}
    """
    text_params.set_text(info_text)


# Ana güncelleme fonksiyonu - duty_cycle ve symmetry değer atamaları iyileştirildi
def update(val=None):
    global vpp_val, freq_val, volt_div_val, time_div_val, signal_type_val, duty_cycle_val, symmetry_val
    vpp_val = slider_vpp.val
    freq_val = slider_freq.val
    volt_div_val = slider_volt_div.val
    time_div_val = slider_time_div.val

    # Slider'dan güncel değerleri al
    if signal_type_val == 'square':
        duty_cycle_val = slider_duty.val
    elif signal_type_val == 'triangle':
        symmetry_val = slider_symmetry.val

    # Sinyal tipini belirle
    if signal_type_val == 'sine':
        t, y = calculate_signal(vpp_val, freq_val, time_div_val, 'sine')
    elif signal_type_val == 'square':
        t, y = calculate_signal(vpp_val, freq_val, time_div_val, 'square', duty_cycle_val)
    elif signal_type_val == 'triangle':
        t, y = calculate_signal(vpp_val, freq_val, time_div_val, 'triangle', 50, symmetry_val)

    line.set_data(t, y)

    setup_grid(volt_div_val, time_div_val)
    update_info_text()
    fig.canvas.draw_idle()


# Kontrol paneli oluşturma - daha fazla alan için alt boşluğu arttır
plt.subplots_adjust(bottom=0.5)

# Slider'lar için pozisyonlar
ax_vpp = plt.axes([0.25, 0.2, 0.5, 0.03])
ax_freq = plt.axes([0.25, 0.15, 0.5, 0.03])
ax_volt_div = plt.axes([0.25, 0.1, 0.5, 0.03])
ax_time_div = plt.axes([0.25, 0.05, 0.5, 0.03])

# Slider'lar
slider_vpp = Slider(ax_vpp, 'Vpp (V)', 0.1, 20.0, valinit=initial_vpp, valstep=0.1)
slider_freq = Slider(ax_freq, 'Frekans (Hz)', 10, 10000, valinit=initial_freq, valstep=10)
slider_volt_div = Slider(ax_volt_div, 'Volt/Div (V)', 0.1, 10.0, valinit=initial_volt_div, valstep=0.1)
slider_time_div = Slider(ax_time_div, 'Time/Div (ms)', 0.01, 1.0, valinit=initial_time_div, valstep=0.01)
# Ekstra açıklama ekleyelim
ax_time_div.text(1.01, 0.5, '(500μs = 0.5ms)', verticalalignment='center', horizontalalignment='left', fontsize=8)

# Metin kutuları için pozisyonlar
ax_vpp_text = plt.axes([0.8, 0.2, 0.15, 0.03])
ax_freq_text = plt.axes([0.8, 0.15, 0.15, 0.03])
ax_volt_div_text = plt.axes([0.8, 0.1, 0.15, 0.03])
ax_time_div_text = plt.axes([0.8, 0.05, 0.15, 0.03])

# Metin kutuları
text_vpp = TextBox(ax_vpp_text, '', initial=str(initial_vpp),
                   color='black', hovercolor='darkgray', label_pad=0.1)
text_freq = TextBox(ax_freq_text, '', initial=str(initial_freq),
                    color='black', hovercolor='darkgray', label_pad=0.1)
text_volt_div = TextBox(ax_volt_div_text, '', initial=str(initial_volt_div),
                        color='black', hovercolor='darkgray', label_pad=0.1)
text_time_div = TextBox(ax_time_div_text, '', initial=str(initial_time_div),
                        color='black', hovercolor='darkgray', label_pad=0.1)

# Metin kutularının arka planını ayarla
for textbox in [text_vpp, text_freq, text_volt_div, text_time_div]:
    textbox.label.set_color('white')  # Etiket rengini beyaz yap
    textbox.text_disp.set_color('yellow')  # Metin rengini sarı yap
    textbox.text_disp.set_fontweight('bold')  # Metni kalın yap

# Sinyal tipi için radio butonları - pozisyonu yukarı taşındı
rax = plt.axes([0.05, 0.15, 0.15, 0.15], facecolor='darkgray')
radio = RadioButtons(rax, ('Sinüs', 'Kare', 'Üçgen'), active=0)

# Duty cycle ve symmetry için slider'lar - daha yukarı çekildi
ax_duty = plt.axes([0.25, 0.02, 0.5, 0.03])
ax_symmetry = plt.axes([0.25, 0.06, 0.5, 0.03])

# Metin kutuları için pozisyonlar (duty cycle ve symmetry için de)
ax_duty_text = plt.axes([0.8, 0.02, 0.15, 0.03])
ax_symmetry_text = plt.axes([0.8, 0.06, 0.15, 0.03])

# Duty cycle ve symmetry slider'ları
slider_duty = Slider(ax_duty, 'Duty Cycle (%)', 0, 100, valinit=50, valstep=1)
slider_symmetry = Slider(ax_symmetry, 'Symmetry (%)', 0, 100, valinit=50, valstep=1)

# Duty cycle ve symmetry için metin kutuları
text_duty = TextBox(ax_duty_text, '', initial='50',
                    color='black', hovercolor='darkgray', label_pad=0.1)
text_symmetry = TextBox(ax_symmetry_text, '', initial='50',
                        color='black', hovercolor='darkgray', label_pad=0.1)

# Metin kutularının arka planını ayarla (duty cycle ve symmetry için de)
for textbox in [text_duty, text_symmetry]:
    textbox.label.set_color('white')  # Etiket rengini beyaz yap
    textbox.text_disp.set_color('yellow')  # Metin rengini sarı yap
    textbox.text_disp.set_fontweight('bold')  # Metni kalın yap


# Güncelleme fonksiyonları
def text_vpp_on_submit(val):
    try:
        new_val = float(val)
        if 0.1 <= new_val <= 20.0:
            slider_vpp.set_val(new_val)
        else:
            text_vpp.set_val(str(slider_vpp.val))  # Geçersiz değer, önceki değere dön
    except ValueError:
        text_vpp.set_val(str(slider_vpp.val))  # Sayı değilse, önceki değere dön


def text_freq_on_submit(val):
    try:
        new_val = float(val)
        if 10 <= new_val <= 10000:
            # En yakın 10'a yuvarla
            new_val = round(new_val / 10) * 10
            slider_freq.set_val(new_val)
        else:
            text_freq.set_val(str(int(slider_freq.val)))
    except ValueError:
        text_freq.set_val(str(int(slider_freq.val)))


def text_volt_div_on_submit(val):
    try:
        new_val = float(val)
        if 0.1 <= new_val <= 10.0:
            slider_volt_div.set_val(new_val)
        else:
            text_volt_div.set_val(str(slider_volt_div.val))
    except ValueError:
        text_volt_div.set_val(str(slider_volt_div.val))


def text_time_div_on_submit(val):
    try:
        new_val = float(val)
        if 0.01 <= new_val <= 1.0:
            slider_time_div.set_val(new_val)
        else:
            text_time_div.set_val(str(slider_time_div.val))
    except ValueError:
        text_time_div.set_val(str(slider_time_div.val))


# Duty cycle ve symmetry güncelleme
def text_duty_on_submit(val):
    try:
        new_val = float(val)
        if 0 <= new_val <= 100:
            slider_duty.set_val(new_val)
        else:
            text_duty.set_val(str(int(slider_duty.val)))
    except ValueError:
        text_duty.set_val(str(int(slider_duty.val)))


def text_symmetry_on_submit(val):
    try:
        new_val = float(val)
        if 0 <= new_val <= 100:
            slider_symmetry.set_val(new_val)
        else:
            text_symmetry.set_val(str(int(slider_symmetry.val)))
    except ValueError:
        text_symmetry.set_val(str(int(slider_symmetry.val)))


# Metin kutusu olayları
text_vpp.on_submit(text_vpp_on_submit)
text_freq.on_submit(text_freq_on_submit)
text_volt_div.on_submit(text_volt_div_on_submit)
text_time_div.on_submit(text_time_div_on_submit)
text_duty.on_submit(text_duty_on_submit)
text_symmetry.on_submit(text_symmetry_on_submit)


# Slider değerleri değiştiğinde metin kutularını güncelleme
def update_text_from_slider_vpp(val):
    text_vpp.set_val(f"{val:.1f}")
    update(val)


def update_text_from_slider_freq(val):
    text_freq.set_val(f"{int(val)}")
    update(val)


def update_text_from_slider_volt_div(val):
    text_volt_div.set_val(f"{val:.1f}")
    update(val)


def update_text_from_slider_time_div(val):
    text_time_div.set_val(f"{val:.3f}")
    update(val)


# Slider değerleri değiştiğinde metin kutularını güncelleme (duty cycle ve symmetry için de)
def update_text_from_slider_duty(val):
    global duty_cycle_val
    duty_cycle_val = val
    text_duty.set_val(f"{int(val)}")
    update(val)


def update_text_from_slider_symmetry(val):
    global symmetry_val
    symmetry_val = val
    text_symmetry.set_val(f"{int(val)}")
    update(val)


# Slider olaylarını güncelleme
slider_vpp.on_changed(update_text_from_slider_vpp)
slider_freq.on_changed(update_text_from_slider_freq)
slider_volt_div.on_changed(update_text_from_slider_volt_div)
slider_time_div.on_changed(update_text_from_slider_time_div)
slider_duty.on_changed(update_text_from_slider_duty)
slider_symmetry.on_changed(update_text_from_slider_symmetry)


# Sinyal tipi seçimi için fonksiyon - slider event'leri düzeltildi
def signal_type_change(label):
    global signal_type_val, duty_cycle_val, symmetry_val
    if label == 'Sinüs':
        signal_type_val = 'sine'
        # Sinüs dalgası için duty cycle ve symmetry ayarlarını devre dışı bırak
        ax_duty.set_visible(False)
        ax_duty_text.set_visible(False)
        ax_symmetry.set_visible(False)
        ax_symmetry_text.set_visible(False)
    elif label == 'Kare':
        signal_type_val = 'square'
        # Kare dalga için duty cycle etkin, symmetry devre dışı
        ax_duty.set_visible(True)
        ax_duty_text.set_visible(True)
        ax_symmetry.set_visible(False)
        ax_symmetry_text.set_visible(False)
        duty_cycle_val = slider_duty.val
    elif label == 'Üçgen':
        signal_type_val = 'triangle'
        # Üçgen dalga için symmetry etkin, duty cycle devre dışı
        ax_duty.set_visible(False)
        ax_duty_text.set_visible(False)
        ax_symmetry.set_visible(True)
        ax_symmetry_text.set_visible(True)
        symmetry_val = slider_symmetry.val

    # Grafik güncellemesi yap
    plt.draw()
    update(None)


# Radio butonları olayı
radio.on_clicked(signal_type_change)

# Başlangıçta duty cycle ve symmetry ayarlarını gizle (başlangıçta sinüs dalgası seçili)
ax_duty.set_visible(False)
ax_duty_text.set_visible(False)
ax_symmetry.set_visible(False)
ax_symmetry_text.set_visible(False)

# Ekran görüntüsünü kaydetme butonu - pozisyonu güncellendi
ax_save = plt.axes([0.25, -0.02, 0.20, 0.025])
button_save = Button(ax_save, 'Ekran Görüntüsünü Kaydet', color='darkgreen', hovercolor='green')


def save_screenshot(event):
    # Geçerli slider değerleriyle dosya adını oluştur
    signal_type_str = "sine" if signal_type_val == 'sine' else f"square_duty{duty_cycle_val}" if signal_type_val == 'square' else f"triangle_sym{symmetry_val}"
    filename = f"osiloskop_{signal_type_str}_vpp{vpp_val}_freq{freq_val}_voltdiv{volt_div_val}_timediv{time_div_val}.png"
    fig.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"{filename} başarıyla kaydedildi.")


button_save.on_clicked(save_screenshot)

# Kontrol panelini düzenle
ax_controls.axis('off')
ax_controls.text(0.02, 0.5, "Kontrol Paneli", fontsize=14, color='white')

# Ayarları gösterme
info_text = f"""
Sinyal: Sinüs
Vpp: {vpp_val:.1f} V
Frekans: {freq_val:.0f} Hz
Volt/Div: {volt_div_val:.1f} V
Time/Div: {time_div_val:.3f} ms
"""
text_params = ax_scope.text(0.02, 0.98, info_text, transform=ax_scope.transAxes, fontsize=10, color='white',
                            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='black', alpha=0.5))

# İlk görüntülemeyi yap
setup_grid(initial_volt_div, initial_time_div)
update(None)

plt.tight_layout()
plt.show()