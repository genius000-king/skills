# عقد الإصدار الثالث

امتداد لعقد الإصدار الثاني؛ `version: 3`. البناء يدعم بيانات 1 و2 للتوافق.

## مصدر العمل

```json
{
  "source": {
    "mode": "existing",
    "identityStatus": "defined",
    "reference": "صفحات ومكونات المصدر التي فُحصت",
    "fidelity": "source",
    "allowIdentityChange": false,
    "identity": {"colors": ["#ffffff", "#245cb7"], "fonts": ["اسم خط المشروع"]}
  }
}
```

`mode`: new/existing. `identityStatus`: defined/undefined. للمشروع القائم
`fidelity`: source عند استخدام المصدر، أو reconstructed عند إعادة البناء من
مرجع محدود. لا يعد هذا الحقل دليلًا على التطابق؛ يلزم تحقق بصري فعلي.
الهوية المحددة تُحفظ، وتُرفض أسئلة palette/typography للمشروع القائم ما لم تسمح
`allowIdentityChange` بتغيير طلبه المستخدم. source.reference وصف المرجع، دون أسرار.

إذا الهوية undefined والعمل interface/mixed/video/motion، أول ثلاثة أسئلة
`kind`: palette، typography، direction، بهذا الترتيب. بقية kinds وصفية مثل
layout/navigation/motion. للأسئلة والخيارات نفس بقية عقد v2.

`caption` اختياري لكل بديل (≤80 حرفًا)، و`helper` للسؤال (≤120). اعرض الفرق
المحدد فقط. التعليل والشرح والتضحية موجودة في تفاصيل مغلقة؛ المحاور لا تعرض.
لأسئلة palette/typography يسمح نفس HTML مع CSS مختلف فعليًا؛ اختلاف الخط/اللون
هو القرار نفسه. بدائل البنية تحتاج patches مختلفة وليست تغيير CSS تجميليًا.

## نسخة الصفحة في الخيار

`visual.scope: page` يجعل القالب يرسم **الصفحة الفعلية** مع patch البديل وبقية
الاختيارات الحالية في المقاس المختار. ينتقل للمجموعة المتأثرة عند تحميلها.
`visual.html/css` تبقى مطلوبة للتوافق، ويمكن إعادة استخدام preview. للعنصر الصغير
استخدم `scope: component` أو أغفله؛ `preview` نفس مكوّن patch الفعلي.

## مواصفات الصفحات وخريطتها

كل screen يضيف `purpose` و`route` (نصوص)، `sections` و`actions` (قوائم نصوص)،
و`when` اختياري على خيارات صحيحة. `position: {x,y}` اختياري لإحداثيات الكانفس
من 0 إلى 20000. لا تؤثر الإحداثيات في تقسيم محتوى الصفحة.

```json
{
  "flow": {
    "entry": "home",
    "edges": [{"id":"home-detail","from":"home","to":"detail","trigger":"فتح المشروع"}]
  }
}
```

flow مطلوب للواجهات والعمل المختلط. endpoints صفحات موجودة وIDs فريدة، وتقبل
edges شروط when. الدورات مسموحة في التنقل، بخلاف تبعيات مهام التنفيذ.
أضف `data-nav="detail"` إلى الزر الفعلي أو `href="#page-detail"` للرابط.
المعاينة تنفّذ الانتقال فقط إذا المسار موجود وفعال. الروابط غير الفعالة تُخفى.
التصدير المستقل يجمع الصفحات الفعالة ويفعّل الربط بينها داخل HTML.

الكانفس يعرض HTML/CSS نفسه كمصغرات، يسمح بالسحب والتكبير وترتيب العقد وفتح الصفحة.
مبدّل المقاس في الكانفس يعرض كل عقدة بنسبة viewport الفعلية: 390×780 رأسيًا
أو 1280×800 أفقيًا، دون قصها داخل إطار واحد ثابت. التحجيم للعرض فقط، وiframe
نفسه يعمل بالأبعاد المحددة. فتح الصفحة يستخدم المقاس المختار نفسه.
تُحفظ ملاحظات الصفحات في `pageNotes` بمفتاح screen.id، ومواقع العقد في
`canvasPositions`، ويصدرها selection version3. --selection يقبلها عند الجولة التالية.

## الصور والخطوط

يمكن استخدام صور PNG/JPEG/WebP/GIF كـ`data:image/...;base64,...` في img أو CSS url،
وبصمة binary صحيحة؛ لا URLs خارجية أو SVG data URI أو scripts من بيانات المشروع.
SVG ثابت داخل HTML مسموح بالقيود الأصلية. CSS url(#id) مسموح لمراجع SVG المحلية.

`fonts`: قائمة `{family,format,weight,data}`. data هي base64 للخط المرخّص؛ formats:
woff2/woff/truetype/opentype، حتى 3MB لكل خط. weight أحد 400/500/600/700/100 900.
أسماء العائلات أحرف وأرقام ومسافات وشرطات، وتطابق الاستخدام في CSS. تستخدم
المعاينات @font-face مبنيًا من هذه البيانات. الخطوط لا تغيّر خط إطار المختبر.
الخطوط المضمّنة في المثال Noto Kufi Arabic وNoto Naskh Arabic، بترخيص assets/fonts/LICENSE.txt.
