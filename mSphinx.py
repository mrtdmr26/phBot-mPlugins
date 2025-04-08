from phBot import *
from threading import Timer
import QtBind

pName = 'mSphinx'
pVersion = '1.0.1'
pURL = 'https://github.com/mrtdmr26/phBot-mPlugins'

# ______________________________ Initializing ______________________________ #
gui = QtBind.init(__name__, pName)

# --- GUI Öğeleri ---
lblTitle = QtBind.createLabel(gui, "Sphinx Reflect Counter", 10, 10)
lblInstructions = QtBind.createLabel(gui,
    "Bu script, reflect buff paketlerini yakalar (opcode 0xB070) ve\n"
    "farklı data[3] değerlerini listeler. Seçili değerin timer süresini\n"
    "güncelleyebilirsiniz.", 10, 30)
lstReflectValues = QtBind.createList(gui, 10, 70, 220, 120)

lblSetTimer = QtBind.createLabel(gui, "Seçili reflect değeri için timer (saniye):", 10, 200)
lineEditTimer = QtBind.createLineEdit(gui, "", 10, 220, 50, 20)
btnUpdateTimer = QtBind.createButton(gui, "update_timer", "Güncelle", 70, 220)

# --- Global Değişkenler ---
# Varsayılan timer ayarları: data[3] değeri : timer süresi (saniye)
reflect_timers = {
    0x99: 16.0,  # Beginne-R
    0x9D: 16.0,  # Beginner
    0x9F: 21.0,  # Intermediate-R
    0xA4: 21.0,  # Intermediate
    0xA5: 26.0,  # Advanced-R
    0xAB: 26.0   # Advanced
}
# Başlangıçta, varsayılan değerleri de içerecek şekilde reflect_values kümesini oluşturuyoruz.
reflect_values = set(reflect_timers.keys())

# --- Yardımcı Fonksiyonlar ---
def updateReflectList():
    """
    reflect_values kümesindeki değerleri sıralı olarak GUI listesini günceller.
    Her bir değer için tanımlı timer süresi de gösterilir.
    """
    QtBind.clear(gui, lstReflectValues)
    for val in sorted(reflect_values):
        timer_val = reflect_timers.get(val, "Ayarlanmadı")
        QtBind.append(gui, lstReflectValues, "0x{:02X} -> {}s".format(val, timer_val))

def update_timer():
    """
    GUI'de seçili olan reflect değerinin timer süresini, lineEditTimer'dan alınan değere günceller.
    """
    selected_index = QtBind.currentIndex(gui, lstReflectValues)
    sorted_values = sorted(reflect_values)
    if selected_index is None or selected_index < 0 or selected_index >= len(sorted_values):
        log("Hiçbir reflect değeri seçilmedi.")
        return
    selected_val = sorted_values[selected_index]
    try:
        new_timer = float(QtBind.text(gui, lineEditTimer))
        reflect_timers[selected_val] = new_timer
        log("0x{:02X} değeri için timer {} saniyeye güncellendi.".format(selected_val, new_timer))
        updateReflectList()
    except Exception as e:
        log("Timer güncellenirken hata: " + str(e))

def lstReflectValues_changed():
    """
    GUI listesindeki seçim değiştiğinde, seçili değerin timer'ını lineEdit'e yazar.
    """
    selected_index = QtBind.currentIndex(gui, lstReflectValues)
    sorted_values = sorted(reflect_values)
    if selected_index is not None and 0 <= selected_index < len(sorted_values):
        selected_val = sorted_values[selected_index]
        current_timer = reflect_timers.get(selected_val, "")
        QtBind.setText(gui, lineEditTimer, str(current_timer))
    else:
        QtBind.setText(gui, lineEditTimer, "")

# --- Packet Yakalama Fonksiyonu ---
def handle_joymax(opcode, data):
    """
    Opcode 0xB070 paketlerini yakalar, sabit kontroller:
      data[0] == 1, data[1] == 0x00, data[4] == 0x7A
    Bu şart sağlanıyorsa, data[3] değeri reflect buff kodunu belirtir.
    Tanımlı timer süresi varsa bot durdurulur ve timer süresi kadar bekledikten sonra yeniden başlatılır.
    Ayrıca, gelen data[3] değeri GUI listesinin güncellenmesi için saklanır.
    """
    if opcode == 0xB070 and get_status() == 'botting':
        if data[0] == 1 and data[1] == 0x00 and data[4] == 0x7A:
            # Eğer data[3] yeni ise, varsayılan timer değeri olarak 0.0 ayarla
            if data[3] not in reflect_timers:
                reflect_timers[data[3]] = 0.0
            reflect_values.add(data[3])
            updateReflectList()
            timer_duration = reflect_timers.get(data[3])
            if timer_duration > 0.0:
                stop_bot()
                log("Reflect buff algılandı (data[3]={}). Bot {} saniye durdu.".format(hex(data[3]), timer_duration))
                Timer(timer_duration, start_bot, ()).start()
    return True

# Başlangıçta varsayılan değerleri GUI listesine ekle
updateReflectList()

log(pName + " başarılı şekilde yüklendi.")
