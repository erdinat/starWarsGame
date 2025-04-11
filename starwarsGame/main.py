import pygame
import sys
import heapq
from collections import deque
from queue import Queue
import math

# Renkler ve sabitler
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
DARK_RED = (139, 0, 0)
ORANGE = (255, 165, 0)
CELL_SIZE = 60
MARGIN = 3

class Lokasyon:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if isinstance(other, Lokasyon):
            return self.x == other.x and self.y == other.y
        return False
    
    def __hash__(self):
        return hash((self.x, self.y))

    def getX(self): return self.x
    def getY(self): return self.y
    def setX(self, x): self.x = x
    def setY(self, y): self.y = y

class Karakter:
    def __init__(self, ad, tur, konum):
        self.ad = ad
        self.tur = tur
        self.konum = konum
        self.can = 0
        self.max_can = 0

    def getAd(self): return self.ad
    def setAd(self, ad): self.ad = ad
    
    def getTur(self): return self.tur
    def setTur(self, tur): self.tur = tur
    
    def getKonum(self): return self.konum
    def setKonum(self, konum): self.konum = konum
    
    def getCan(self): return self.can
    def setCan(self, can): self.can = can

    def enKisaYol(self, hedef, labirent):
        """
        Bu metod kötü karakterler tarafından override edilecek
        """
        pass

class LukeSkywalker(Karakter):
    def __init__(self, konum):
        super().__init__("Luke Skywalker", "İyi", konum)
        self.can = 3
        self.max_can = 3

class MasterYoda(Karakter):
    def __init__(self, konum):
        super().__init__("Master Yoda", "İyi", konum)
        self.can = 6
        self.max_can = 6

class Stormtrooper(Karakter):
    def __init__(self, konum):
        super().__init__("Stormtrooper", "Kötü", konum)
    
    def enKisaYol(self, hedef, labirent):
        """
        BFS algoritması ile en kısa yolu bulur.
        Sadece geçerli yolları (0) kullanır ve dört yönde hareket eder.
        """
        baslangic = (self.konum.getY(), self.konum.getX())
        hedef_konum = (hedef.getY(), hedef.getX())
        
        # Kuyruk yapısı: [[konum], ziyaret_edilmis]
        queue = deque([[baslangic]])
        ziyaret_edilmis = {baslangic}
        
        # Dört yön: yukarı, aşağı, sol, sağ
        yonler = [(-1,0), (1,0), (0,-1), (0,1)]
        
        while queue:
            yol = queue.popleft()
            current = yol[-1]
            
            # Hedefe ulaştık mı?
            if current == hedef_konum:
                return yol
            
            # Her yönü kontrol et
            for dy, dx in yonler:
                ny, nx = current[0] + dy, current[1] + dx
                
                # Sınırlar içinde mi?
                if 0 <= ny < len(labirent) and 0 <= nx < len(labirent[0]):
                    # Geçerli yol mu? (0 veya hedef)
                    if ((labirent[ny][nx] == '0' or (ny, nx) == hedef_konum) and 
                        (ny, nx) not in ziyaret_edilmis):
                        # Yeni konumu yola ekle
                        yeni_yol = list(yol)
                        yeni_yol.append((ny, nx))
                        queue.append(yeni_yol)
                        ziyaret_edilmis.add((ny, nx))
        
        return None  # Yol bulunamadı

class DarthVader(Karakter):
    def __init__(self, konum):
        super().__init__("Darth Vader", "Kötü", konum)
    
    def enKisaYol(self, hedef, labirent):
        """
        Dijkstra algoritması ile en kısa yolu bulur.
        Duvarları yok sayar - sadece sınır kontrolü yapar.
        """
        baslangic = (self.konum.getY(), self.konum.getX())
        hedef_konum = (hedef.getY(), hedef.getX())
        
        # Mesafe ve önceki düğüm bilgisi
        mesafeler = {baslangic: 0}
        onceki = {baslangic: None}
        ziyaret_edilmis = set()
        
        # Öncelik kuyruğu (mesafe, konum)
        queue = [(0, baslangic)]
        
        while queue:
            mesafe, current = heapq.heappop(queue)
            
            if current in ziyaret_edilmis:
                continue
                
            ziyaret_edilmis.add(current)
            
            if current == hedef_konum:
                break
            
            # Dört yön: yukarı, aşağı, sol, sağ
            for dy, dx in [(-1,0), (1,0), (0,-1), (0,1)]:
                ny, nx = current[0] + dy, current[1] + dx
                
                # Sadece sınır kontrolü yap - duvarları yok say
                if 0 <= ny < len(labirent) and 0 <= nx < len(labirent[0]):
                    yeni_konum = (ny, nx)
                    yeni_mesafe = mesafe + 1
                    
                    if yeni_konum not in mesafeler or yeni_mesafe < mesafeler[yeni_konum]:
                        mesafeler[yeni_konum] = yeni_mesafe
                        onceki[yeni_konum] = current
                        heapq.heappush(queue, (yeni_mesafe, yeni_konum))
        
        # Yolu oluştur
        if hedef_konum in onceki:
            yol = []
            current = hedef_konum
            while current is not None:
                yol.append(current)
                current = onceki[current]
            return yol[::-1]  # Yolu tersine çevir
        
        return None

    def _mesafeHesapla(self, konum1, konum2):
        """Manhattan mesafesini hesaplar"""
        return abs(konum1[0] - konum2[0]) + abs(konum1[1] - konum2[1])

class KyloRen(Karakter):
    def __init__(self, konum):
        super().__init__("Kylo Ren", "Kötü", konum)
    
    def enKisaYol(self, hedef, labirent):
        """
        İki adımlı BFS algoritması ile en kısa yolu bulur.
        Her harekette iki kare ilerler.
        """
        baslangic = (self.konum.getY(), self.konum.getX())
        hedef_konum = (hedef.getY(), hedef.getX())
        
        queue = deque([[baslangic]])
        ziyaret_edilmis = {baslangic}
        
        # İki adımlık yönler: yukarı, aşağı, sol, sağ
        yonler = [(-2,0), (2,0), (0,-2), (0,2)]
        
        while queue:
            yol = queue.popleft()
            current = yol[-1]
            
            # Hedefe ulaştık mı?
            if current == hedef_konum:
                return yol
            
            # Her yönü kontrol et
            for dy, dx in yonler:
                ny, nx = current[0] + dy, current[1] + dx
                
                # Sınırlar içinde mi?
                if 0 <= ny < len(labirent) and 0 <= nx < len(labirent[0]):
                    # Ara noktayı kontrol et (bir adım)
                    ara_y, ara_x = current[0] + dy//2, current[1] + dx//2
                    
                    # Hem ara nokta hem de hedef nokta geçerli yol mu?
                    if (labirent[ara_y][ara_x] != '1' and 
                        (labirent[ny][nx] != '1' or (ny, nx) == hedef_konum) and 
                        (ny, nx) not in ziyaret_edilmis):
                        
                        # Yeni konumu yola ekle
                        yeni_yol = list(yol)
                        yeni_yol.append((ny, nx))
                        queue.append(yeni_yol)
                        ziyaret_edilmis.add((ny, nx))
        
        # Hedef çok uzaksa veya ulaşılamıyorsa, normal hareket et
        if not queue:
            return self._normalHareket(hedef, labirent)
        
        return None

    def _normalHareket(self, hedef, labirent):
        """
        Normal (tek adımlı) BFS algoritması ile yedek yol bulur
        """
        baslangic = (self.konum.getY(), self.konum.getX())
        hedef_konum = (hedef.getY(), hedef.getX())
        
        queue = deque([[baslangic]])
        ziyaret_edilmis = {baslangic}
        
        # Normal yönler
        yonler = [(-1,0), (1,0), (0,-1), (0,1)]
        
        while queue:
            yol = queue.popleft()
            current = yol[-1]
            
            if current == hedef_konum:
                return yol
            
            for dy, dx in yonler:
                ny, nx = current[0] + dy, current[1] + dx
                
                if (0 <= ny < len(labirent) and 0 <= nx < len(labirent[0]) and
                    (labirent[ny][nx] != '1' or (ny, nx) == hedef_konum) and
                    (ny, nx) not in ziyaret_edilmis):
                    
                    yeni_yol = list(yol)
                    yeni_yol.append((ny, nx))
                    queue.append(yeni_yol)
                    ziyaret_edilmis.add((ny, nx))
        
        return None

class Oyun:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()  # Ses sistemini başlat
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Star Wars Labirent")
        self.clock = pygame.time.Clock()
        self.menu_aktif = True
        self.oyun_aktif = False
        self.font = pygame.font.Font(None, 36)
        self.FPS = 60
        
        # Ses efektlerini yükle
        try:
            self.sesler = {
                'menu_sec': pygame.mixer.Sound('sesler/menu_sec.wav'),
                'menu_onay': pygame.mixer.Sound('sesler/menu_onay.wav'),
                'hareket': pygame.mixer.Sound('sesler/hareket.wav'),
                'hasar': pygame.mixer.Sound('sesler/hasar.wav'),
                'kazanma': pygame.mixer.Sound('sesler/kazanma.wav'),
                'kaybetme': pygame.mixer.Sound('sesler/kaybetme.wav')
            }
        except:
            print("Ses dosyaları yüklenemedi!")
            self.sesler = None

        # Genişletilmiş menü seçenekleri
        self.menu_items = [
            {"text": "Luke Skywalker ile Oyna (3 Can)", "action": lambda: self.oyunu_baslat(LukeSkywalker)},
            {"text": "Master Yoda ile Oyna (6 Can)", "action": lambda: self.oyunu_baslat(MasterYoda)},
            {"text": "Kontroller", "action": self.kontrolleri_goster},
            {"text": "Yardım", "action": self.yardim_goster},
            {"text": "Çıkış", "action": sys.exit}
        ]
        self.selected_item = 0

    def ses_cal(self, ses_adi):
        """Belirtilen ses efektini çalar"""
        if self.sesler and ses_adi in self.sesler:
            self.sesler[ses_adi].play()

    def haritaYukle(self, dosya):
        """
        Haritayı ve karakter konumlarını yükler
        Format:
        Karakter:DarthVader,Kapi:A
        Karakter:KyloRen,Kapi:B
        Karakter:Stormtrooper,Kapi:A
        0 0 0 0 1 0 0 0 0 0 0 0 1 0
        ...
        """
        try:
            with open(dosya, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines()]

            # Karakter ve kapı bilgilerini oku
            self.karakter_bilgileri = []
            line_index = 0
            while line_index < len(lines) and 'Karakter:' in lines[line_index]:
                line = lines[line_index].strip()
                karakter_info = {}
                for part in line.split(','):
                    if 'Karakter:' in part:
                        karakter_info['karakter'] = part.split(':')[1].strip()
                    elif 'Kapi:' in part:
                        karakter_info['kapi'] = part.split(':')[1].strip()
                self.karakter_bilgileri.append(karakter_info)
                line_index += 1

            # Labirent matrisini oku
            self.labirent = []
            for line in lines[line_index:]:
                if line.strip():
                    line = ' '.join(line.split())
                    self.labirent.append(line.split())

            # Boyut kontrolü
            self.ROWS = len(self.labirent)
            self.COLS = len(self.labirent[0])
            if self.COLS != 14 or self.ROWS != 11:
                raise ValueError(f"Harita boyutları 14x11 olmalı! Mevcut: {self.COLS}x{self.ROWS}")

            # Kapıları yerleştir - x ve y koordinatlarını düzelttik
            self.kapilar = {
                'A': Lokasyon(4, 0),    # x=4, y=0 (üst kapı)
                'B': Lokasyon(4, 10)    # x=4, y=10 (alt kapı)
            }

            # Başlangıç ve hedef noktaları - x ve y koordinatlarını düzelttik
            self.baslangic = Lokasyon(6, 5)   # x=6, y=5 (orta nokta)
            self.hedef = Lokasyon(4, 10)      # x=4, y=10 (B kapısı ile aynı)

            # İşaretlemeler - koordinat sistemini düzelttik
            for kapi, konum in self.kapilar.items():
                self.labirent[konum.getY()][konum.getX()] = kapi
            self.labirent[self.baslangic.getY()][self.baslangic.getX()] = 'S'
            self.labirent[self.hedef.getY()][self.hedef.getX()] = 'T'

            return self.labirent

        except Exception as e:
            print(f"Harita yükleme hatası: {str(e)}")
            raise

    def oyunuHazirla(self, karakter_class):
        """
        Seçilen karaktere ve harita.txt'deki bilgilere göre oyunu hazırlar
        """
        # İyi karakteri oluştur
        self.iyi_karakter = karakter_class(self.baslangic)
        
        # Kötü karakterleri oluştur
        self.kotu_karakterler = []
        for bilgi in self.karakter_bilgileri:
            karakter_type = bilgi["karakter"]
            kapi = bilgi["kapi"]
            
            if kapi in self.kapilar:
                konum = self.kapilar[kapi]
                if karakter_type == "DarthVader":
                    self.kotu_karakterler.append(DarthVader(konum))
                elif karakter_type == "KyloRen":
                    self.kotu_karakterler.append(KyloRen(konum))
                elif karakter_type == "Stormtrooper":
                    self.kotu_karakterler.append(Stormtrooper(konum))

    def oyunu_baslat(self, karakter_class):
        """
        Seçilen karakterle oyunu başlatır
        """
        try:
            self.menu_aktif = False
            self.oyun_aktif = True
            
            # Haritayı yükle
            self.labirent = self.haritaYukle("harita.txt")
            
            # Pencere boyutunu ayarla
            pencere_genislik = self.COLS * CELL_SIZE
            pencere_yukseklik = self.ROWS * CELL_SIZE + 50  # Can barı için ekstra alan
            self.pencere = pygame.display.set_mode((pencere_genislik, pencere_yukseklik))
            
            # Oyunu hazırla ve başlat
            self.oyunuHazirla(karakter_class)
            self.oyunDongusu()
            
        except Exception as e:
            print(f"Oyun başlatma hatası: {str(e)}")
            self.menu_aktif = True
            self.oyun_aktif = False

    def oyunDongusu(self):
        """Ana oyun döngüsü"""
        hareket_zamani = pygame.time.get_ticks()
        HAREKET_GECIKMESI = 200
        
        while self.oyun_aktif:
            current_time = pygame.time.get_ticks()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.oyun_duraklatildi_goster()

            if current_time - hareket_zamani >= HAREKET_GECIKMESI:
                # İyi karakter hareketi
                keys = pygame.key.get_pressed()
                x, y = self.iyi_karakter.getKonum().getX(), self.iyi_karakter.getKonum().getY()
                yeni_x, yeni_y = x, y
                hareket_var = False

                # Karakter hareketi
                if keys[pygame.K_UP] and y > 0 and self.labirent[y-1][x] != '1':
                    yeni_y -= 1
                    hareket_var = True
                elif keys[pygame.K_DOWN] and y < self.ROWS-1 and self.labirent[y+1][x] != '1':
                    yeni_y += 1
                    hareket_var = True
                elif keys[pygame.K_LEFT] and x > 0 and self.labirent[y][x-1] != '1':
                    yeni_x -= 1
                    hareket_var = True
                elif keys[pygame.K_RIGHT] and x < self.COLS-1 and self.labirent[y][x+1] != '1':
                    yeni_x += 1
                    hareket_var = True

                if hareket_var:
                    self.iyi_karakter.getKonum().setX(yeni_x)
                    self.iyi_karakter.getKonum().setY(yeni_y)
                    
                    # Kötü karakterlerin hareketi
                    for kotu in self.kotu_karakterler:
                        yol = kotu.enKisaYol(self.iyi_karakter.getKonum(), self.labirent)
                        if yol and len(yol) > 1:
                            next_pos = yol[1]  # Bir sonraki adım
                            kotu.getKonum().setY(next_pos[0])
                            kotu.getKonum().setX(next_pos[1])
                    
                    # Çarpışma kontrolü
                    if self.carpismaKontrol():
                        continue

                    hareket_zamani = current_time

                self.ciz()
                self.clock.tick(self.FPS)

    def ciz(self):
        self.pencere.fill(WHITE)
        
        # Labirent çizimi
        for i in range(len(self.labirent)):
            for j in range(len(self.labirent[i])):
                rect = pygame.Rect(j*CELL_SIZE, i*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                cell = self.labirent[i][j]
                
                # Önce tüm hücrelere beyaz arka plan çiz
                pygame.draw.rect(self.pencere, WHITE, rect)
                
                # Hücre tipine göre çizim
                if cell == '1':  # Duvar
                    # Duvarları daha belirgin yap
                    pygame.draw.rect(self.pencere, BLACK, rect)
                    # Duvar kenarlarına gri çerçeve ekle
                    pygame.draw.rect(self.pencere, (64, 64, 64), rect, 2)
                elif cell == '0':  # Yol
                    # Yollara hafif gri arka plan ekle
                    pygame.draw.rect(self.pencere, (240, 240, 240), rect)
                    # Izgara çizgileri ekle
                    pygame.draw.rect(self.pencere, (200, 200, 200), rect, 1)
                elif cell == 'T':  # Hedef
                    pygame.draw.rect(self.pencere, (200, 255, 200), rect)  # Açık yeşil arka plan
                    pygame.draw.rect(self.pencere, GREEN, rect, 2)  # Yeşil çerçeve
                    text = self.font.render('⭐', True, BLACK)
                    text_rect = text.get_rect(center=(j*CELL_SIZE + CELL_SIZE//2,
                                                    i*CELL_SIZE + CELL_SIZE//2))
                    self.pencere.blit(text, text_rect)
                elif cell in ['A', 'B']:  # Kapılar
                    # Kapılara gradyan efekti ekle
                    pygame.draw.rect(self.pencere, (100, 100, 255), rect)  # Koyu mavi
                    pygame.draw.rect(self.pencere, BLUE, rect, 3)  # Mavi çerçeve
                    text = self.font.render(cell, True, WHITE)
                    text_rect = text.get_rect(center=(j*CELL_SIZE + CELL_SIZE//2,
                                                    i*CELL_SIZE + CELL_SIZE//2))
                    self.pencere.blit(text, text_rect)

        # Başlangıç noktası
        baslangic_rect = pygame.Rect(6*CELL_SIZE, 5*CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.pencere, (255, 255, 200), baslangic_rect)  # Açık sarı arka plan
        pygame.draw.rect(self.pencere, YELLOW, baslangic_rect, 2)  # Sarı çerçeve
        
        # İyi karakter çizimi
        if self.iyi_karakter:
            x = self.iyi_karakter.getKonum().getX() * CELL_SIZE
            y = self.iyi_karakter.getKonum().getY() * CELL_SIZE
            color = RED if isinstance(self.iyi_karakter, LukeSkywalker) else GREEN
            pygame.draw.circle(self.pencere, color,
                             (x + CELL_SIZE//2, y + CELL_SIZE//2),
                             CELL_SIZE//2 - MARGIN)
            
            # Karakter adı - font boyutu artırıldı
            isim_font = pygame.font.Font(None, 30)  # 20'den 30'a çıkarıldı
            text = isim_font.render(self.iyi_karakter.getAd(), True, WHITE)
            text_rect = text.get_rect(center=(x + CELL_SIZE//2, y - 10))  # Biraz daha yukarı çekildi
            # Arka plan ekle
            bg_rect = text_rect.copy()
            bg_rect.inflate_ip(14, 8)  # Arka plan marjını artırdık
            pygame.draw.rect(self.pencere, BLACK, bg_rect)
            self.pencere.blit(text, text_rect)
        
        # Kötü karakterler çizimi
        for kotu in self.kotu_karakterler:
            x = kotu.getKonum().getX() * CELL_SIZE
            y = kotu.getKonum().getY() * CELL_SIZE
            
            # Karakter tipine göre renk seç
            if isinstance(kotu, DarthVader):
                color = DARK_RED
            elif isinstance(kotu, KyloRen):
                color = PURPLE
            else:
                color = BLACK
            
            pygame.draw.circle(self.pencere, color,
                             (x + CELL_SIZE//2, y + CELL_SIZE//2),
                             CELL_SIZE//2 - MARGIN)
            
            # Karakter adı - font boyutu artırıldı
            isim_font = pygame.font.Font(None, 30)  # 20'den 30'a çıkarıldı
            text = isim_font.render(kotu.getAd(), True, WHITE)
            text_rect = text.get_rect(center=(x + CELL_SIZE//2, y - 10))
            # Arka plan ekle
            bg_rect = text_rect.copy()
            bg_rect.inflate_ip(14, 8)  # Arka plan marjını artırdık
            pygame.draw.rect(self.pencere, BLACK, bg_rect)
            self.pencere.blit(text, text_rect)
            
            # Mesafe göstergesi - font boyutu artırıldı
            if path := kotu.enKisaYol(self.iyi_karakter.getKonum(), self.labirent):
                mesafe = len(path) - 1
                mesafe_text = isim_font.render(f"Mesafe: {mesafe}", True, WHITE)
                mesafe_rect = mesafe_text.get_rect(center=(x + CELL_SIZE//2, y + CELL_SIZE + 10))
                bg_rect = mesafe_rect.copy()
                bg_rect.inflate_ip(14, 8)  # Arka plan marjını artırdık
                pygame.draw.rect(self.pencere, BLACK, bg_rect)
                self.pencere.blit(mesafe_text, mesafe_rect)
        
        # Can göstergesi
        can_y = self.ROWS * CELL_SIZE + 10
        can_height = 30
        can_width = int((self.iyi_karakter.getCan() / self.iyi_karakter.max_can) * self.COLS*CELL_SIZE)
        pygame.draw.rect(self.pencere, RED, (0, can_y, self.COLS*CELL_SIZE, can_height))
        pygame.draw.rect(self.pencere, GREEN, (0, can_y, can_width, can_height))
        
        # Can miktarını ondalıklı göster (Master Yoda için)
        if isinstance(self.iyi_karakter, MasterYoda):
            can_text = f"Can: {self.iyi_karakter.getCan():.1f}/{self.iyi_karakter.max_can}"
        else:
            can_text = f"Can: {int(self.iyi_karakter.getCan())}/{self.iyi_karakter.max_can}"
        
        text = self.font.render(can_text, True, BLACK)
        text_rect = text.get_rect(center=(self.COLS*CELL_SIZE//2, can_y + can_height//2))
        self.pencere.blit(text, text_rect)
        
        pygame.display.flip()

    def sonuc_ekrani(self, basarili):
        """Oyun sonuç ekranı"""
        # Star Wars temalı renkler
        STAR_WARS_YELLOW = (255, 232, 31)
        LIGHTSABER_GREEN = (0, 255, 0)
        LIGHTSABER_RED = (255, 0, 0)

        # Animasyon için değişkenler
        animation_duration = 3  # 3 saniye
        start_time = pygame.time.get_ticks() / 1000
        
        while (pygame.time.get_ticks() / 1000 - start_time) < animation_duration:
            current_time = pygame.time.get_ticks() / 1000
            progress = (current_time - start_time) / animation_duration
            pulse = (math.sin(current_time * 5) + 1) / 2  # Yanıp sönme efekti
            
            # Arkaplan gradyanı
            self.pencere.fill(BLACK)
            if basarili:
                # Kazanma durumunda yeşil tonlarında gradyan
                for i in range(self.ROWS * CELL_SIZE + 50):
                    color = (0, max(0, min(255, i // 3)), 0)
                    pygame.draw.line(self.pencere, color, (0, i), (self.COLS * CELL_SIZE, i))
            else:
                # Kaybetme durumunda kırmızı tonlarında gradyan
                for i in range(self.ROWS * CELL_SIZE + 50):
                    color = (max(0, min(255, i // 3)), 0, 0)
                    pygame.draw.line(self.pencere, color, (0, i), (self.COLS * CELL_SIZE, i))

            # Başlık
            baslik = "TEBRİKLER! KAZANDINIZ!" if basarili else "GAME OVER!"
            baslik_color = LIGHTSABER_GREEN if basarili else LIGHTSABER_RED
            baslik_font = pygame.font.Font(None, 72)
            
            # Başlık efektleri
            baslik_alpha = int(255 * min(1, progress * 2))  # Fade-in efekti
            baslik_offset = math.sin(current_time * 3) * 5  # Yukarı-aşağı hareket
            
            # Başlık gölgesi
            baslik_shadow = baslik_font.render(baslik, True, BLACK)
            baslik_shadow.set_alpha(baslik_alpha)
            baslik_shadow_rect = baslik_shadow.get_rect(center=(self.COLS*CELL_SIZE//2 + 3, self.ROWS*CELL_SIZE//3 + 3 + baslik_offset))
            self.pencere.blit(baslik_shadow, baslik_shadow_rect)
            
            # Başlık metni
            baslik_surface = baslik_font.render(baslik, True, baslik_color)
            baslik_surface.set_alpha(baslik_alpha)
            baslik_rect = baslik_surface.get_rect(center=(self.COLS*CELL_SIZE//2, self.ROWS*CELL_SIZE//3 + baslik_offset))
            self.pencere.blit(baslik_surface, baslik_rect)

            # Karakter mesajı
            mesaj = f"{self.iyi_karakter.getAd()} başarıyla görevi tamamladı!" if basarili else f"{self.iyi_karakter.getAd()} yenildi!"
            mesaj_color = STAR_WARS_YELLOW
            mesaj_font = pygame.font.Font(None, 48)
            mesaj_surface = mesaj_font.render(mesaj, True, mesaj_color)
            mesaj_surface.set_alpha(int(255 * min(1, progress * 3)))
            mesaj_rect = mesaj_surface.get_rect(center=(self.COLS*CELL_SIZE//2, self.ROWS*CELL_SIZE//2))
            self.pencere.blit(mesaj_surface, mesaj_rect)

            # Devam mesajı
            if progress > 0.7:  # Son 30% zamanında göster
                devam_alpha = int(255 * pulse)  # Yanıp sönme efekti
                devam_text = self.font.render("Menüye dönmek için bekleyin...", True, WHITE)
                devam_text.set_alpha(devam_alpha)
                devam_rect = devam_text.get_rect(center=(self.COLS*CELL_SIZE//2, self.ROWS*CELL_SIZE - 50))
                self.pencere.blit(devam_text, devam_rect)

            pygame.display.flip()
            self.clock.tick(60)

        # 3 saniye sonra menüye dön
        pygame.time.wait(500)  # Ekstra 0.5 saniye bekle

    def kontrolleri_goster(self):
        """Oyun kontrollerini gösteren ekran"""
        kontroller_aktif = True
        STAR_WARS_YELLOW = (255, 232, 31)
        STAR_WARS_BLUE = (30, 144, 255)
        
        baslik = "KONTROLLER"
        kontroller = [
            ("^", "Yukarı hareket"),
            ("v", "Aşağı hareket"),
            ("<", "Sola hareket"),
            (">", "Sağa hareket"),
            ("ESC", "Menüye dön"),
        ]
        
        baslik_font = pygame.font.Font(None, 72)
        tus_font = pygame.font.Font(None, 48)
        aciklama_font = pygame.font.Font(None, 36)

        while kontroller_aktif:
            current_time = pygame.time.get_ticks() / 1000
            pulse = (math.sin(current_time * 2) + 1) / 2  # Yanıp sönme efekti
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_RETURN, pygame.K_ESCAPE]:
                        kontroller_aktif = False

            # Arkaplan gradyanı
            self.screen.fill(BLACK)
            for i in range(600):
                color = (max(0, min(255, i // 4)), max(0, min(255, i // 4)), max(0, min(255, i // 2)))
                pygame.draw.line(self.screen, color, (0, i), (800, i))

            # Başlık
            baslik_shadow = baslik_font.render(baslik, True, BLACK)
            baslik_text = baslik_font.render(baslik, True, STAR_WARS_YELLOW)
            baslik_rect = baslik_text.get_rect(center=(400, 100))
            self.screen.blit(baslik_shadow, (baslik_rect.x + 3, baslik_rect.y + 3))
            self.screen.blit(baslik_text, baslik_rect)

            # Dekoratif çizgiler
            line_color = (int(200 * pulse + 55), int(200 * pulse + 55), 255)
            pygame.draw.line(self.screen, line_color, (100, 150), (700, 150), 2)
            pygame.draw.line(self.screen, line_color, (150, 155), (650, 155), 1)

            # Kontroller
            for i, (tus, aciklama) in enumerate(kontroller):
                # Tuş kutusu
                box_rect = pygame.Rect(250, 200 + i * 60, 50, 50)
                pygame.draw.rect(self.screen, STAR_WARS_BLUE, box_rect, 3)
                
                # Tuş metni
                tus_text = tus_font.render(tus, True, WHITE)
                tus_rect = tus_text.get_rect(center=box_rect.center)
                self.screen.blit(tus_text, tus_rect)
                
                # Açıklama
                aciklama_text = aciklama_font.render(aciklama, True, STAR_WARS_YELLOW)
                aciklama_rect = aciklama_text.get_rect(midleft=(320, 225 + i * 60))
                self.screen.blit(aciklama_text, aciklama_rect)

            # Alt bilgi
            devam_text = aciklama_font.render("Devam etmek için ENTER'a basın", True, WHITE)
            devam_rect = devam_text.get_rect(center=(400, 550))
            devam_text.set_alpha(int(255 * pulse))  # Yanıp sönme efekti
            self.screen.blit(devam_text, devam_rect)

            pygame.display.flip()
            self.clock.tick(60)

    def yardim_goster(self):
        """Oyun hakkında yardım ve bilgi ekranı"""
        yardim_aktif = True
        STAR_WARS_YELLOW = (255, 232, 31)
        STAR_WARS_BLUE = (30, 144, 255)
        LIGHTSABER_GREEN = (0, 255, 0)
        LIGHTSABER_RED = (255, 0, 0)

        baslik = "YARDIM"
        baslik_font = pygame.font.Font(None, 72)
        alt_baslik_font = pygame.font.Font(None, 48)
        aciklama_font = pygame.font.Font(None, 36)

        karakterler = [
            ("Luke Skywalker", "3 can hakkı", LIGHTSABER_RED),
            ("Master Yoda", "6 can hakkı (Yarım hasar alır)", LIGHTSABER_GREEN)
        ]

        dusmanlar = [
            ("Darth Vader", "Duvarlardan geçebilir", DARK_RED),
            ("Kylo Ren", "İki adım hareket eder", PURPLE),
            ("Stormtrooper", "Normal hareket eder", BLACK)
        ]

        while yardim_aktif:
            current_time = pygame.time.get_ticks() / 1000
            pulse = (math.sin(current_time * 2) + 1) / 2  # Yanıp sönme efekti
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_RETURN, pygame.K_ESCAPE]:
                        yardim_aktif = False

            # Arkaplan gradyanı
            self.screen.fill(BLACK)
            for i in range(600):
                color = (max(0, min(255, i // 4)), max(0, min(255, i // 4)), max(0, min(255, i // 2)))
                pygame.draw.line(self.screen, color, (0, i), (800, i))

            # Başlık
            baslik_shadow = baslik_font.render(baslik, True, BLACK)
            baslik_text = baslik_font.render(baslik, True, STAR_WARS_YELLOW)
            baslik_rect = baslik_text.get_rect(center=(400, 80))
            self.screen.blit(baslik_shadow, (baslik_rect.x + 3, baslik_rect.y + 3))
            self.screen.blit(baslik_text, baslik_rect)

            # Dekoratif çizgiler
            line_color = (int(200 * pulse + 55), int(200 * pulse + 55), 255)
            pygame.draw.line(self.screen, line_color, (100, 130), (700, 130), 2)
            pygame.draw.line(self.screen, line_color, (150, 135), (650, 135), 1)

            # Oyun Amacı
            amac_text = alt_baslik_font.render("Oyun Amacı", True, STAR_WARS_BLUE)
            amac_rect = amac_text.get_rect(center=(400, 180))
            self.screen.blit(amac_text, amac_rect)
            
            hedef_text = aciklama_font.render("Hedefe (*) ulaşırken düşmanlardan kaçın!", True, WHITE)  # Yıldız karakteri değiştirildi
            hedef_rect = hedef_text.get_rect(center=(400, 220))
            self.screen.blit(hedef_text, hedef_rect)

            # Karakterler
            karakter_baslik = alt_baslik_font.render("Karakterler", True, STAR_WARS_BLUE)
            self.screen.blit(karakter_baslik, (50, 280))

            for i, (ad, ozellik, renk) in enumerate(karakterler):
                # Karakter simgesi
                pygame.draw.circle(self.screen, renk, (80, 340 + i * 50), 15)
                
                # Karakter adı ve özelliği
                ad_text = aciklama_font.render(f"{ad}:", True, STAR_WARS_YELLOW)
                ozellik_text = aciklama_font.render(ozellik, True, WHITE)
                self.screen.blit(ad_text, (110, 330 + i * 50))
                self.screen.blit(ozellik_text, (350, 330 + i * 50))

            # Düşmanlar
            dusman_baslik = alt_baslik_font.render("Düşmanlar", True, STAR_WARS_BLUE)
            self.screen.blit(dusman_baslik, (50, 430))

            for i, (ad, ozellik, renk) in enumerate(dusmanlar):
                # Düşman simgesi
                pygame.draw.circle(self.screen, renk, (80, 490 + i * 50), 15)
                
                # Düşman adı ve özelliği
                ad_text = aciklama_font.render(f"{ad}:", True, STAR_WARS_YELLOW)
                ozellik_text = aciklama_font.render(ozellik, True, WHITE)
                self.screen.blit(ad_text, (110, 480 + i * 50))
                self.screen.blit(ozellik_text, (350, 480 + i * 50))

            # Alt bilgi
            devam_text = aciklama_font.render("Devam etmek için ENTER'a basın", True, WHITE)
            devam_rect = devam_text.get_rect(center=(400, 570))
            devam_text.set_alpha(int(255 * pulse))  # Yanıp sönme efekti
            self.screen.blit(devam_text, devam_rect)

            pygame.display.flip()
            self.clock.tick(60)

    def oyun_duraklatildi_goster(self):
        """Oyun duraklatıldığında gösterilecek ekran"""
        duraklat_menu = [
            {"text": "Devam Et", "action": lambda: None},
            {"text": "Menüye Dön", "action": self.menuye_don},
            {"text": "Çıkış", "action": sys.exit}
        ]
        secili = 0

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        secili = (secili - 1) % len(duraklat_menu)
                        self.ses_cal('menu_sec')
                    elif event.key == pygame.K_DOWN:
                        secili = (secili + 1) % len(duraklat_menu)
                        self.ses_cal('menu_sec')
                    elif event.key == pygame.K_RETURN:
                        self.ses_cal('menu_onay')
                        if secili == 0:  # Devam Et
                            return
                        duraklat_menu[secili]["action"]()
                    elif event.key == pygame.K_ESCAPE:
                        return

            # Yarı saydam siyah arka plan
            s = pygame.Surface((self.COLS*CELL_SIZE, self.ROWS*CELL_SIZE))
            s.set_alpha(128)
            s.fill(BLACK)
            self.pencere.blit(s, (0,0))

            # Menü seçenekleri
            for i, item in enumerate(duraklat_menu):
                color = RED if i == secili else WHITE
                text = self.font.render(item["text"], True, color)
                rect = text.get_rect(center=(self.COLS*CELL_SIZE//2, self.ROWS*CELL_SIZE//2 - 50 + i * 50))
                self.pencere.blit(text, rect)

            pygame.display.flip()
            self.clock.tick(30)

    def menuye_don(self):
        """Oyunu durdurup menüye döner"""
        self.oyun_aktif = False
        self.menu_aktif = True
        
        # Pencere boyutunu menü için yeniden ayarla
        self.screen = pygame.display.set_mode((800, 600))

    def menu_dongusu(self):
        """Ana menü döngüsü"""
        # Star Wars temalı renkler
        STAR_WARS_YELLOW = (255, 232, 31)
        STAR_WARS_BLUE = (30, 144, 255)
        LIGHTSABER_RED = (255, 0, 0)
        LIGHTSABER_GREEN = (0, 255, 0)
        
        # Menü başlığı
        baslik = "STAR WARS"
        alt_baslik = "LABİRENT OYUNU"
        baslik_font = pygame.font.Font(None, 72)
        alt_baslik_font = pygame.font.Font(None, 48)

        # Animasyon için değişkenler
        pulse = 0
        pulse_speed = 0.05
        title_offset = 0
        title_speed = 0.5

        while self.menu_aktif:
            current_time = pygame.time.get_ticks() / 1000  # Saniye cinsinden zaman
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected_item = (self.selected_item - 1) % len(self.menu_items)
                        self.ses_cal('menu_sec')
                    elif event.key == pygame.K_DOWN:
                        self.selected_item = (self.selected_item + 1) % len(self.menu_items)
                        self.ses_cal('menu_sec')
                    elif event.key == pygame.K_RETURN:
                        self.ses_cal('menu_onay')
                        self.menu_items[self.selected_item]["action"]()

            # Arkaplan gradyanı
            self.screen.fill(BLACK)
            for i in range(600):
                color = (max(0, min(255, i // 3)), max(0, min(255, i // 4)), max(0, min(255, i // 2)))
                pygame.draw.line(self.screen, color, (0, i), (800, i))

            # Başlık animasyonu
            pulse = (math.sin(current_time * pulse_speed) + 1) / 2  # 0 ile 1 arası
            title_offset = math.sin(current_time * title_speed) * 5  # -5 ile 5 arası

            # Başlık çizimi
            baslik_shadow = baslik_font.render(baslik, True, BLACK)
            baslik_surface = baslik_font.render(baslik, True, STAR_WARS_YELLOW)
            baslik_rect = baslik_surface.get_rect(center=(400, 80 + title_offset))
            
            # Gölge efekti
            self.screen.blit(baslik_shadow, (baslik_rect.x + 3, baslik_rect.y + 3))
            self.screen.blit(baslik_surface, baslik_rect)

            # Alt başlık
            alt_baslik_surface = alt_baslik_font.render(alt_baslik, True, STAR_WARS_BLUE)
            alt_baslik_rect = alt_baslik_surface.get_rect(center=(400, 140))
            self.screen.blit(alt_baslik_surface, alt_baslik_rect)

            # Dekoratif çizgiler
            line_color = (int(200 * pulse + 55), int(200 * pulse + 55), 255)
            pygame.draw.line(self.screen, line_color, (100, 180), (700, 180), 2)
            pygame.draw.line(self.screen, line_color, (150, 185), (650, 185), 1)
            
            # Menü seçenekleri
            for i, item in enumerate(self.menu_items):
                if i == self.selected_item:
                    # Seçili öğe için ışın kılıcı efekti
                    glow_surface = pygame.Surface((400, 40), pygame.SRCALPHA)
                    glow_color = LIGHTSABER_RED if "Luke" in item["text"] else LIGHTSABER_GREEN
                    pygame.draw.rect(glow_surface, (*glow_color, 100), (0, 0, 400, 40))
                    self.screen.blit(glow_surface, (200, 235 + i * 50))
                    
                    color = WHITE
                    # Seçili öğe için parıltı efekti
                    text_color = (255, 255, 255)
                else:
                    color = (200, 200, 200)
                    text_color = (180, 180, 180)

                text = self.font.render(item["text"], True, color)
                rect = text.get_rect(center=(400, 250 + i * 50))
                
                # Seçili öğe için gölge efekti
                if i == self.selected_item:
                    glow = self.font.render(item["text"], True, text_color)
                    glow_rect = glow.get_rect(center=(400, 250 + i * 50))
                    self.screen.blit(glow, (glow_rect.x + 2, glow_rect.y + 2))
                
                self.screen.blit(text, rect)
            
            pygame.display.flip()
            self.clock.tick(60)

    def carpismaKontrol(self):
        """Çarpışma kontrolü ve hasar hesaplama"""
        for kotu in self.kotu_karakterler:
            if (kotu.getKonum().getX() == self.iyi_karakter.getKonum().getX() and 
                kotu.getKonum().getY() == self.iyi_karakter.getKonum().getY()):
                
                # Mevcut canı al
                mevcut_can = float(self.iyi_karakter.getCan())
                
                # Karakter tipine göre hasar uygula
                if isinstance(self.iyi_karakter, MasterYoda):
                    yeni_can = mevcut_can - 0.5
                else:  # Luke Skywalker
                    yeni_can = mevcut_can - 1.0
                
                # Yeni can değerini ayarla
                self.iyi_karakter.setCan(yeni_can)
                self.ses_cal('hasar')
                
                # Can kontrolü
                if yeni_can <= 0:
                    self.iyi_karakter.setCan(0)  # Canı 0'a sabitle
                    self.ses_cal('kaybetme')
                    self.sonuc_ekrani(False)  # Game Over
                    self.menuye_don()
                    return True
                
                # Karakteri başlangıç noktasına geri döndür - koordinatları doğrudan atıyoruz
                baslangic_konum = Lokasyon(6, 5)  # Başlangıç konumu net olarak tanımla
                self.iyi_karakter.setKonum(baslangic_konum)
                
                # Konumun doğru ayarlandığını kontrol et (güvenlik amaçlı)
                if self.iyi_karakter.getKonum().getX() != 6 or self.iyi_karakter.getKonum().getY() != 5:
                    print("Konum düzeltiliyor...")
                    self.iyi_karakter.getKonum().setX(6)
                    self.iyi_karakter.getKonum().setY(5)
                
                return True
                
        # Hedefe ulaşma kontrolü
        if (self.iyi_karakter.getKonum().getX() == self.hedef.getX() and 
            self.iyi_karakter.getKonum().getY() == self.hedef.getY()):
            self.ses_cal('kazanma')
            self.sonuc_ekrani(True)
            self.menuye_don()
            return True
            
        return False

# Ana program başlangıcı
if __name__ == "__main__":
    try:
        oyun = Oyun()
        oyun.menu_dongusu()
    except Exception as e:
        print(f"Hata: {str(e)}")
    finally:
        pygame.quit()
        sys.exit()