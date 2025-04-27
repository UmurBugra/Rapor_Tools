import matplotlib.pyplot as plt
import numpy as np

# Bu genelde benim raporlarımda grafik çizdirmek için kullandığım bir fonksiyon.

saniye = [0.05, 0.1, 0.5, 1, 3, 5, 10, 50, 100]

gerilim = [0.12, 0.16, 0.28, 0.4, 0.64, 1.56, 2.56, 2.64, 3.12]

plt.figure(figsize=(10, 6), dpi=200)
plt.axhline(0, color='black', linewidth=0.5)
plt.axvline(0, color='black', linewidth=0.5)


plt.xticks(np.arange(0, 110, 10))
plt.yticks(np.arange(0, 3.6, 0.2))


plt.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray', alpha=0.5)


plt.plot(saniye, gerilim, marker='o', linestyle='-', color='b')  # Deşarj için kırmızı renk kullanıldı

plt.title("Yüksek Geçiren Filtre Eğrisi")
plt.xlabel("Frekans (kHz)")
plt.ylabel("Gerilim (V)")

plt.show()