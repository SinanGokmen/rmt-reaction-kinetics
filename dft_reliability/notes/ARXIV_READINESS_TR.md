# DFT veri güvenilirliği çalışması — 11 Eylül 2026

## Araştırmanın odağı

Ana soru: Büyük bir DFT veri kümesinde, sınırlı yeniden hesaplama bütçesiyle hangi
kayıtları denetlemeliyiz? Ana makale bu soruya göre yeniden yazıldı. Önceki
kuvvet-gürültüsü düzeltme deneyi destekleyici malzeme olarak korundu.

Kalite kontrolünün daha önce araştırılmadığı iddia edilmiyor. Carbogno ve
arkadaşları sayısal hata ve baz kümesi eksikliği modellemesini, Bosoni ve
arkadaşları kodlar arası hassasiyet denetimini, Kuryla ve arkadaşları moleküler
DFT kuvvetlerinin sıkı referanslardan sapmasını araştırdı. Mahshook ve Banerjee
ise model açıklamaları ve hedefli ilk-prensip hesaplarıyla eğitim verisi
incelemesini ele aldı. Atıflar makalede yer alıyor.

Burada incelenen katkı, fiziksel kontrollerin matematiksel sınırları ile toplam
referans bütçesi ve hata sayısı/hata etkisi ayrımının aynı karşılaştırmada
kullanılmasıdır. Bunun ilk uygulama olduğu veya literatürdeki tüm yakın
çalışmaların tüketildiği iddia edilmiyor.

## Yapılmış deney

Kuryla ve arkadaşlarının yayımladığı AIMNet2 ve Transition1x eşleştirilmiş
örneklemlerindeki toplam 2.000 konfigürasyon kullanıldı. Yeni DFT çalıştırılmadı;
denetim, mevcut sıkı referansın seçildiğinde açığa çıkarılmasıyla simüle edildi.

Öğrenen yöntemler için ortalama %20 referans başlangıç kümesi ve kalan havuzun
%10'u kullanıldı. Toplam ortalama bütçe %28,04. Doğrudan fiziksel yöntemlere de
aynı toplam kayıt sayısını seçme hakkı verildi. Eğitim referansları ücretsiz
sayılmadı. Beş senaryo formül bazında ayrılıyor, ancak birbiriyle örtüşüyor;
bağımsız tekrar gibi yorumlanmıyor.

AIMNet2'de kuvvet/tork kontrolü, en yüksek fark gösteren %10'luk grubun %95'ini
buldu. Ridge ve MP-kovaryanslı ridge %77,6 buldu. Transition1x'te aynı fiziksel
kontrol %31,8, log-hata ağaç modeli %39,0 buldu; ağaç sonucunun senaryo aralığı
%20–49. Yöntem üstünlüğü veri kümesine ve hata hedefine bağlı.

Transition1x'in toplam karesel farkının %97,75'ini tek kayıt oluşturuyor.
Kuvvet/tork ve net-kuvvet kontrolleri bu kaydı tüm ana bütçelerde kaçırıyor.
Kuvvet büyüklüğüne göre seçim onu buluyor, ancak yüksek hatalı kayıtların genel
sayısını bulmada güçlü değil. Bu, hata sayısı ile hata etkisinin ayrı hedefler
olduğuna somut bir örnek. Kaynak verideki farkın keşfi bize atfedilmiyor.

## Matematik ve RMT

Kuvvet/tork ihlali, uygun varsayımlarla toplam kuvvet hatasına alt sınır verir.
Küçük ihlal, toplam hataya sonlu üst sınır vermez; simetriyi sağlayan bileşende
büyük hata bulunabilir. İkinci ifade, eşit maliyetli seçimde en yüksek hata
olasılıklı kayıtların beklenen bulgu sayısını maksimize ettiğini ve olasılık
kestirimindeki düzgün epsilon hatasının en fazla 2k epsilon kayba yol açtığını
gösterir. Bunlar standart matematiksel argümanların uygulamalarıdır. Deneydeki
skorların kalibre olasılıklar olduğu gösterilmedi.

RMT'den esinlenen karşılaştırıcı, betimleyici kovaryansının küçük özdeğerlerini
havuzluyor. Bu matris doğrudan DFT gürültüsü kovaryansı değildir ve MP varsayımları
doğrulanmadı. Sonuçlar özel bir RMT üstünlüğü göstermiyor. RMT'yi başarılı ilan
etmek için negatif sonuçlar çıkarılmadı.

## Yayın açısından durum

Derlenmiş makale, üç sonuç şekli, tablo, ispatlar, kaynakça ve tekrarlanabilir
kod mevcut. Veri sızıntısı, geometri dönüşümü altında betimleyici değişmezliği,
kayıt sayıları ve kaydedilmiş tahminlerden ana sonuçların yeniden hesaplanması
kontrol edildi. Bu kontroller bağımsız bilimsel doğrulama yerine geçmez.

Bu bir sınırlı örneklem üzerinde yöntem karşılaştırmasıdır. Yüz binlerce
malzemenin denetlendiği, deneysel doğruluğun ölçüldüğü veya daha iyi bir ilaç
keşif modeli geliştirildiği söylenemez. Güçlü bir sonraki kanıt, yeni bir bağımsız
eşleştirilmiş veri kümesinde, gerçek hesap maliyetlerini ve keşif kararlarını
ölçen ileriye dönük bir denetim olacaktır. Mevcut sonuçların özgünlük ve önem
bakımından arXiv moderasyonunu geçeceği garanti edilemez.

## Yazar, biçim ve AI açıklaması

Sinan Gökmen; Department of Chemistry, Istanbul Technical University;
gokmens23@itu.edu.tr. Metinde ChatGPT/Codex'in araştırma sorusu, matematik,
kod, deneyler, literatür taraması ve yazımdaki kapsamlı yardımı açıkça belirtildi.
Tamamlanmış bir bağımsız insan incelemesi varmış gibi ifade kullanılmadı.

11 Eylül 2026'da kontrol edilen
[arXiv moderasyon politikası](https://info.arxiv.org/help/moderation/index.html),
önemli üretken AI kullanımının açıklanmasını, araçların yazar yapılmamasını ve
adı yazılan yazarın içerikten sorumlu olmasını gerektiriyor. AI açıklaması tek
başına tüm gönderim koşullarının sağlandığı veya kabul garantisi anlamına gelmez.
Gönderim yapılmadı. Kullanıcı GitHub yayımına yeniden izin verdi; genel analiz
deposu bağlantısı makaleye eklendi. Bağımsız üçüncü veri doğrulaması tamamlanmadı.


## Ek deney: başlangıç referanslarının maliyeti

Toplam 280 referanslık sabit bütçede, 10, 20, 50, 100 ve tam başlangıç katmanı
(ortalama 200 kayıt) karşılaştırıldı. Her formül katmanında beş iç içe rastgele
başlangıç seçimi kullanıldı. Denetim havuzu sabit tutuldu; yalnızca bu havuzdaki
en yüksek hatalı %10'luk grubun bulunması sayıldı. Eğitim referanslarına bulgu
kredisi verilmedi. Dolayısıyla bu sayıların paydası ana deneyden farklıdır.

AIMNet2 ridge sonucu 50 eğitim referansında %93,7, tam başlangıç katmanında
%71,7. Doğrudan kuvvet/tork kontrolü %95,5 ile yine daha iyi. Transition1x'te
50 referanslı ridge %36,5, rastgele seçim beklentisi %35,1. Küçük referans
bütçesinin her veri kümesinde güçlü bir öğrenilmiş denetleyici ürettiği sonucuna
varılamaz. Daha az eğitim verisinin daha doğru bir tahmin modeli verdiği de
söylenmiyor: ölçülen sonuç, eğitim ve seçim bütçelerinin birlikte etkisidir.

Ek deney önceki sonuçlar görüldükten sonra tasarlandı; yeni bağımsız doğrulama
olarak sunulmuyor. Protokol, tüm seçimler, tahminler ve yeniden hesaplama
kontrolleri pakette korunuyor.
