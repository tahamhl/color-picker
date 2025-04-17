# Color Picker 🎨

Modern ve kullanıcı dostu bir renk seçme aracı. Windows sistemlerde ekrandaki herhangi bir noktanın rengini kolayca yakalayın, düzenleyin ve kopyalayın.

## 🌟 Özellikler

- **Gerçek Zamanlı Renk Takibi**: Fare imlecinin altındaki rengi anında görüntüleme
- **Çoklu Format Desteği**: RGB ve HEX renk kodları
- **Renk Geçmişi**: Son kullanılan 24 rengi otomatik kaydetme
- **Özelleştirilebilir Kısayol Tuşları**: Tüm işlemler için kişiselleştirilebilir klavye kısayolları
- **Renk Düzenleyici**: Yakalanan renkleri parlaklık ve doygunluk ayarlarıyla düzenleme
- **Sistem Tepsisi Desteği**: Arka planda çalışma özelliği
- **Modern Arayüz**: CustomTkinter ile geliştirilmiş şık ve modern tasarım
- **Ekran Görüntüsü**: Tek tuşla ekran görüntüsü alma ve otomatik kaydetme

## 🛠️ Gereksinimler

```
customtkinter
ttkbootstrap
pyautogui
keyboard
pyperclip
Pillow
pystray
```

## 📦 Kurulum

1. Repoyu klonlayın:
```bash
git clone https://github.com/tahamhl/color-picker.git
```

2. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

3. Uygulamayı çalıştırın:
```bash
python color_picker.py
```

## 🎯 Kullanım

1. **Renk Yakalama**:
   - İmleci istediğiniz rengin üzerine getirin
   - Renk önizleme panelinde canlı olarak rengi görün
   - RGB veya HEX formatında kopyalamak için kısayol tuşlarını kullanın

2. **Kısayol Tuşları**:
   - RGB Kopyala: Varsayılan 'R'
   - HEX Kopyala: Varsayılan 'H'
   - İki Format Kopyala: Varsayılan 'B'
   - Ekran Görüntüsü: Varsayılan 'S'
   - Çıkış: Varsayılan 'Q'

3. **Renk Düzenleme**:
   - Geçmiş panelindeki renklere tıklayarak düzenleyiciyi açın
   - Parlaklık ve doygunluk ayarlarını yapın
   - Düzenlenmiş rengi istediğiniz formatta kopyalayın

4. **Sistem Tepsisi**:
   - Pencereyi kapatınca uygulama sistem tepsisine küçülür
   - Sağ tıklayarak menüyü açın
   - "Göster" ile pencereyi tekrar açın
   - "Çıkış" ile uygulamayı tamamen kapatın

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 👨‍💻 Geliştirici

- [Taha Mehel](https://github.com/tahamhl)
- Website: [tahamehel.tr](https://tahamehel.tr)

