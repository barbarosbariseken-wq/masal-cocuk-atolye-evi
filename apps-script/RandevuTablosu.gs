/**
 * MASAL ÇOCUK ATÖLYE EVİ · RANDEVU TABLOSU
 * Web sitesindeki randevu talepleri bu tabloya yazılır; sitede saatler
 *   "Onay bekliyor"  → sarı (Bekliyor)
 *   "Onaylandı"      → kırmızı (Dolu)
 *   "İptal"          → saat yeniden açılır
 * olarak görünür. Telefonla alınan randevular için de bir satır ekleyip Durum'u "Onaylandı" yapın.
 * Bütün günü kapatmak için Saat sütununu boş bırakın.
 * Siteye yalnızca tarih, saat ve durum gider; veli bilgileri sitede görünmez.
 */
var SAYFA = 'Randevular';
var BASLIK = ['Talep zamanı', 'Tarih', 'Saat', 'Durum', 'Hizmet', 'Görüşme şekli', 'Veli', 'Telefon', 'E-posta', 'Çocuk', 'Yaş', 'Not'];
var DURUMLAR = ['Onay bekliyor', 'Onaylandı', 'İptal'];
var TZ = 'Europe/Istanbul';

function kurulum() {
  var ss = SpreadsheetApp.getActive();
  var sh = ss.getSheetByName(SAYFA) || ss.insertSheet(SAYFA, 0);
  sh.getRange(1, 1, 1, BASLIK.length).setValues([BASLIK]).setFontWeight('bold').setBackground('#2F6F62').setFontColor('#FFFFFF');
  sh.setFrozenRows(1);
  sh.getRange('B2:C').setNumberFormat('@');
  sh.getRange('H2:H').setNumberFormat('@');
  var kural = SpreadsheetApp.newDataValidation().requireValueInList(DURUMLAR, true).build();
  sh.getRange('D2:D').setDataValidation(kural);
  var d = sh.getRange('D2:D');
  sh.setConditionalFormatRules([
    SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo('Onay bekliyor').setBackground('#FFF1C9').setRanges([d]).build(),
    SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo('Onaylandı').setBackground('#CFE6DE').setRanges([d]).build(),
    SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo('İptal').setBackground('#E4E8E7').setFontColor('#6B7B86').setRanges([d]).build()
  ]);
  sh.setColumnWidths(1, BASLIK.length, 130);
  var ilk = ss.getSheetByName('Sayfa1') || ss.getSheetByName('Sheet1');
  if (ilk && ilk.getName() !== SAYFA && ilk.getLastRow() === 0) ss.deleteSheet(ilk);
}

function metin(v, bicim) {
  if (v instanceof Date) return Utilities.formatDate(v, TZ, bicim);
  return String(v || '').trim();
}

function json(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}

function kayitlar() {
  var sh = SpreadsheetApp.getActive().getSheetByName(SAYFA);
  if (!sh || sh.getLastRow() < 2) return [];
  var bugun = Utilities.formatDate(new Date(), TZ, 'yyyy-MM-dd');
  return sh.getRange(2, 2, sh.getLastRow() - 1, 3).getValues().map(function (r) {
    var t = metin(r[0], 'yyyy-MM-dd'), s = metin(r[1], 'HH:mm'), du = metin(r[2]);
    if (/^\d:\d\d$/.test(s)) s = '0' + s;
    return { t: t, s: s, du: du };
  }).filter(function (k) {
    return /^\d{4}-\d\d-\d\d$/.test(k.t) && k.t >= bugun && k.du !== 'İptal';
  });
}

// Site saatleri buradan okur (yalnızca tarih, saat, durum).
function doGet() {
  return json({ ok: true, slots: kayitlar().map(function (k) {
    return { t: k.t, s: k.s, d: k.du === 'Onaylandı' ? 'dolu' : 'bekliyor' };
  }) });
}

// Site yeni talebi buraya gönderir.
function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    var v = JSON.parse(e.postData.contents);
    var cakisma = kayitlar().some(function (k) { return k.t === v.tarih && (k.s === v.saat || k.s === ''); });
    if (cakisma) return json({ ok: false, dolu: true });
    var sh = SpreadsheetApp.getActive().getSheetByName(SAYFA);
    sh.appendRow([Utilities.formatDate(new Date(), TZ, 'dd.MM.yyyy HH:mm'), v.tarih, v.saat, 'Onay bekliyor',
      v.hizmet || '', v.sekil || '', v.veli || '', v.telefon || '', v.eposta || '', v.cocuk || '', v.yas || '', v.not || '']);
    return json({ ok: true });
  } catch (err) {
    return json({ ok: false, hata: String(err) });
  } finally {
    lock.releaseLock();
  }
}
