#!/usr/bin/env python3
"""Build the editable SAGE presentation as ODP for LibreOffice conversion."""
from pathlib import Path
from xml.sax.saxutils import escape
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ppt" / "sage.odp"
LOGO = ROOT / "assets" / "sage-logo.png"

NS = """xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
xmlns:xlink="http://www.w3.org/1999/xlink"
xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"
office:version="1.2\""""


def p(text, style="Body"):
    return f'<text:p text:style-name="{style}">{escape(text)}</text:p>'


def textbox(x, y, w, h, text, style="Body", frame="TextFrame"):
    lines = text if isinstance(text, list) else [text]
    body = "".join(p(line, style) for line in lines)
    return (f'<draw:frame draw:style-name="{frame}" svg:x="{x}cm" '
            f'svg:y="{y}cm" svg:width="{w}cm" svg:height="{h}cm">'
            f'<draw:text-box>{body}</draw:text-box></draw:frame>')


def rect(x, y, w, h, style="Card"):
    return (f'<draw:rect draw:style-name="{style}" svg:x="{x}cm" '
            f'svg:y="{y}cm" svg:width="{w}cm" svg:height="{h}cm"/>')


def image(x, y, w, h):
    return (f'<draw:frame draw:style-name="Image" svg:x="{x}cm" '
            f'svg:y="{y}cm" svg:width="{w}cm" svg:height="{h}cm">'
            '<draw:image xlink:href="Pictures/sage-logo.png" '
            'xlink:type="simple" xlink:show="embed" xlink:actuate="onLoad"/>'
            '</draw:frame>')


def footer(n):
    return (textbox(1.2, 18.25, 22, .45, "SAGE · Situation Engineering",
                    "Footer") +
            textbox(31.4, 18.25, 1.2, .45, str(n), "Footer"))


def slide(name, elements, n, dark=False):
    bg = "BackgroundDark" if dark else "Background"
    return (f'<draw:page draw:name="{escape(name)}" draw:style-name="{bg}" '
            'draw:master-page-name="Standard" presentation:presentation-page-layout-name="AL1T0">'
            + elements + footer(n) + '</draw:page>')


slides = []
slides.append(slide("Title",
    image(1.8, 2.2, 10.8, 10.8) +
    textbox(14.0, 4.0, 17.5, 2.3, "SAGE", "Hero") +
    textbox(14.1, 6.5, 17.2, 1.4, "Situation Engineering for Evidence-Applicable AI", "Subtitle") +
    rect(14.1, 8.4, 2.4, .18, "GoldLine") +
    textbox(14.1, 9.2, 16.8, 2.4,
            ["관련된 증거가 지금 이 질문에", "실제로 적용 가능한가?"], "Statement"),
    1))

slides.append(slide("Problem",
    textbox(1.4, 1.0, 30.5, 1.3, "문제: 관련성만으로는 충분하지 않다", "Title") +
    rect(1.5, 3.1, 9.5, 10.8, "Card") +
    rect(12.2, 3.1, 9.5, 10.8, "Card") +
    rect(22.9, 3.1, 9.5, 10.8, "Card") +
    textbox(2.2, 4.0, 8.1, 1.0, "STALE", "CardTitle") +
    textbox(2.2, 5.4, 8.0, 5.8,
            ["과거에는 참이었지만", "질문 시점에는 만료된 사실", "", "→ 시간 상태 필요"], "Body") +
    textbox(12.9, 4.0, 8.1, 1.0, "OUT OF SCOPE", "CardTitle") +
    textbox(12.9, 5.4, 8.0, 5.8,
            ["특정 조직·지역·사용자에게만", "적용되는 국소적 사실", "", "→ 범위 상태 필요"], "Body") +
    textbox(23.6, 4.0, 8.1, 1.0, "WRONG WORLD", "CardTitle") +
    textbox(23.6, 5.4, 8.0, 5.8,
            ["가정·제안·소문을 현실의", "확정 사실로 사용하는 오류", "", "→ 양상·세계 상태 필요"], "Body") +
    textbox(3.0, 15.0, 27.8, 1.2,
            "Situation blindness = 증거는 맞지만 적용 조건이 틀린 실패", "Callout"),
    2))

slides.append(slide("Framework",
    textbox(1.4, 1.0, 30.5, 1.3, "SAGE의 핵심: 명시적 Situation State", "Title") +
    rect(1.7, 4.3, 6.4, 5.0, "CardAccent") +
    rect(10.0, 4.3, 6.4, 5.0, "CardAccent") +
    rect(18.3, 4.3, 6.4, 5.0, "CardAccent") +
    rect(26.6, 4.3, 5.5, 5.0, "CardAccent") +
    textbox(2.2, 5.0, 5.4, 1.0, "1 · SENSE", "CardTitle") +
    textbox(2.2, 6.4, 5.4, 2.0, "질문·증거에서\n상태 변수 추출", "Body") +
    textbox(10.5, 5.0, 5.4, 1.0, "2 · UPDATE", "CardTitle") +
    textbox(10.5, 6.4, 5.4, 2.0, "충돌·변경·취소를\n상태에 반영", "Body") +
    textbox(18.8, 5.0, 5.4, 1.0, "3 · VALIDATE", "CardTitle") +
    textbox(18.8, 6.4, 5.4, 2.0, "시간·범위·출처·\n관찰자·세계 검증", "Body") +
    textbox(27.1, 5.0, 4.5, 1.0, "4 · ACT", "CardTitle") +
    textbox(27.1, 6.4, 4.5, 2.0, "답변 / 검색 /\n질문 / 기권", "Body") +
    textbox(3.0, 11.4, 27.8, 2.2,
            "(q, E) → Ŝ → Ŝ′ → policy → answer", "Equation") +
    textbox(5.0, 14.4, 23.8, 1.2,
            "상황 상태는 prompt·context·memory·tool을 잇는 검증 계층", "Callout"),
    3))

slides.append(slide("Benchmark",
    textbox(1.4, 1.0, 30.5, 1.3, "SituationCatch-Bench", "Title") +
    textbox(1.6, 3.1, 9.0, 3.0, "4,200", "Metric") +
    textbox(1.9, 6.1, 8.5, 1.0, "controlled instances", "MetricLabel") +
    textbox(12.0, 3.1, 9.0, 3.0, "7", "Metric") +
    textbox(12.3, 6.1, 8.5, 1.0, "diagnostic categories", "MetricLabel") +
    textbox(22.4, 3.1, 9.0, 3.0, "600", "Metric") +
    textbox(22.7, 6.1, 8.5, 1.0, "items per category", "MetricLabel") +
    rect(1.8, 8.4, 30.0, 5.3, "Card") +
    textbox(2.6, 9.2, 28.4, 3.8,
            ["Temporal · Hidden premise · Source conflict · Modality",
             "Scope · Observer knowledge · Counterfactual world"], "Statement") +
    textbox(3.3, 14.8, 27.4, 1.3,
            "목적: 자연언어 일반화가 아니라 적용성 불변식의 기계적 진단", "Callout"),
    4))

slides.append(slide("Results",
    textbox(1.4, 1.0, 30.5, 1.3, "상태 품질이 최종 정확도를 결정한다", "Title") +
    rect(2.0, 4.2, 8.6, 9.4, "Card") +
    rect(12.6, 4.2, 8.6, 9.4, "Card") +
    rect(23.2, 4.2, 8.6, 9.4, "Card") +
    textbox(2.7, 5.2, 7.2, 2.0, "100.0%", "MetricGreen") +
    textbox(3.0, 7.7, 6.8, 1.0, "Gold state", "CardTitle") +
    textbox(3.0, 9.2, 6.8, 2.5, "구조화 상태를\n직접 제공", "Body") +
    textbox(13.3, 5.2, 7.2, 2.0, "77.9%", "MetricGold") +
    textbox(13.6, 7.7, 6.8, 1.0, "Predicted state", "CardTitle") +
    textbox(13.6, 9.2, 6.8, 2.5, "claim text에서\n상태를 추출", "Body") +
    textbox(23.9, 5.2, 7.2, 2.0, "35.1%", "MetricRed") +
    textbox(24.2, 7.7, 6.8, 1.0, "Corrupted state", "CardTitle") +
    textbox(24.2, 9.2, 6.8, 2.5, "출처·양상·범위를\n의도적으로 손상", "Body") +
    textbox(4.0, 15.0, 26.0, 1.2,
            "Oracle 성능만으로는 sensing bottleneck을 볼 수 없다", "Callout"),
    5))

slides.append(slide("Architecture",
    textbox(1.4, 1.0, 30.5, 1.3, "SCQA Reference Architecture", "Title") +
    textbox(1.7, 3.1, 14.4, 1.0, "Situation schema", "SectionTitle") +
    rect(1.7, 4.4, 14.4, 9.5, "Card") +
    textbox(2.5, 5.1, 12.8, 7.8,
            ["• actors, entities, events", "• valid time & observation time",
             "• modality & source status", "• scope & observer knowledge",
             "• real / counterfactual world", "• unresolved critical variables"], "Body") +
    textbox(18.0, 3.1, 14.0, 1.0, "Response policy", "SectionTitle") +
    rect(18.0, 4.4, 14.0, 9.5, "Card") +
    textbox(18.8, 5.1, 12.4, 7.8,
            ["ANSWER   상태가 충분하고 일관됨", "RETRIEVE  근거 또는 상태가 부족함",
             "CLARIFY   사용자 변수 확인 필요", "ABSTAIN   신뢰 가능한 판단 불가",
             "", "모든 결정은 provenance와 함께 기록"], "Body") +
    textbox(4.3, 15.0, 25.5, 1.2,
            "소스 구현: code/scqa · 실행 결과: paper/results", "Callout"),
    6))

slides.append(slide("Evidence",
    textbox(1.4, 1.0, 30.5, 1.3, "Evidence ladder: 주장 범위를 분리한다", "Title") +
    rect(2.0, 3.1, 29.8, 11.6, "Card") +
    textbox(3.0, 4.0, 27.8, 9.8,
            ["E1  Formal definition          완료",
             "E2  Oracle-state unit tests     완료 · 4,200 items",
             "E3  Natural prevalence         선행연구가 지지",
             "E4  Predicted-state control    완료 · controlled text",
             "E5  Multi-model intervention   harness 완료 · 실측 미완료",
             "E6  Independent human study    protocol 완료 · 실측 미완료"], "Evidence") +
    textbox(4.0, 15.4, 26.0, 1.1,
            "실행하지 않은 API·사람 평가를 결과처럼 보고하지 않는다", "Callout"),
    7))

slides.append(slide("Reproducibility",
    textbox(1.4, 1.0, 30.5, 1.3, "Reproducibility package", "Title") +
    rect(1.7, 3.3, 9.3, 10.5, "CardAccent") +
    rect(12.2, 3.3, 9.3, 10.5, "CardAccent") +
    rect(22.7, 3.3, 9.3, 10.5, "CardAccent") +
    textbox(2.4, 4.1, 7.9, 1.0, "code/", "CardTitle") +
    textbox(2.4, 5.7, 7.9, 6.7,
            ["SCQA engine", "state sensor", "multi-LLM adapters",
             "annotation workflow", "automated tests"], "Body") +
    textbox(12.9, 4.1, 7.9, 1.0, "paper/", "CardTitle") +
    textbox(12.9, 5.7, 7.9, 6.7,
            ["main.tex", "supplementary.tex", "4,200-item dataset",
             "item-level results", "26 linked references"], "Body") +
    textbox(23.4, 4.1, 7.9, 1.0, "ppt/", "CardTitle") +
    textbox(23.4, 5.7, 7.9, 6.7,
            ["sage.pptx", "editable source", "research narrative",
             "measured outcomes", "limitations"], "Body") +
    textbox(4.0, 15.2, 26.0, 1.2,
            "PYTHONPATH=code python code/run_experiments.py", "Code"),
    8))

slides.append(slide("Closing",
    image(12.7, 1.4, 8.5, 8.5) +
    textbox(4.0, 10.0, 25.9, 1.6,
            "Relevant evidence is not necessarily applicable evidence.", "Closing") +
    textbox(5.0, 12.2, 23.9, 1.2,
            "SAGE makes the active situation explicit, testable, and auditable.", "Subtitle") +
    rect(14.8, 14.5, 4.2, .18, "GoldLine") +
    textbox(9.0, 15.2, 15.8, 1.0, "github.com/leemgs/sage", "Callout"),
    9))

styles = f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document-styles {NS}>
 <office:styles>
  <style:style style:name="Standard" style:family="paragraph"/>
 </office:styles>
 <office:automatic-styles>
  <style:page-layout style:name="PM1"><style:page-layout-properties fo:page-width="33.867cm" fo:page-height="19.05cm" style:print-orientation="landscape"/></style:page-layout>
 </office:automatic-styles>
 <office:master-styles><style:master-page style:name="Standard" style:page-layout-name="PM1"/></office:master-styles>
</office:document-styles>"""

content = f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document-content {NS}>
<office:automatic-styles>
 <style:style style:name="Background" style:family="drawing-page"><style:drawing-page-properties draw:fill="solid" draw:fill-color="#F7F8F5"/></style:style>
 <style:style style:name="BackgroundDark" style:family="drawing-page"><style:drawing-page-properties draw:fill="solid" draw:fill-color="#F7F8F5"/></style:style>
 <style:style style:name="TextFrame" style:family="graphic"><style:graphic-properties draw:stroke="none" draw:fill="none" fo:padding="0cm"/></style:style>
 <style:style style:name="Image" style:family="graphic"><style:graphic-properties draw:stroke="none" draw:fill="none"/></style:style>
 <style:style style:name="Card" style:family="graphic"><style:graphic-properties draw:stroke="solid" svg:stroke-color="#D8E0DB" draw:fill="solid" draw:fill-color="#FFFFFF" draw:corner-radius="0.3cm"/></style:style>
 <style:style style:name="CardAccent" style:family="graphic"><style:graphic-properties draw:stroke="solid" svg:stroke-color="#77A092" draw:fill="solid" draw:fill-color="#EFF5F1" draw:corner-radius="0.3cm"/></style:style>
 <style:style style:name="GoldLine" style:family="graphic"><style:graphic-properties draw:stroke="none" draw:fill="solid" draw:fill-color="#C99222"/></style:style>
 <style:style style:name="Title" style:family="paragraph"><style:paragraph-properties fo:margin-bottom="0cm"/><style:text-properties fo:font-family="Liberation Sans" fo:font-size="28pt" fo:font-weight="bold" fo:color="#092A54"/></style:style>
 <style:style style:name="Hero" style:family="paragraph"><style:text-properties fo:font-family="Liberation Sans" fo:font-size="50pt" fo:font-weight="bold" fo:color="#092A54"/></style:style>
 <style:style style:name="Subtitle" style:family="paragraph"><style:text-properties fo:font-family="Liberation Sans" fo:font-size="18pt" fo:color="#52766F"/></style:style>
 <style:style style:name="Statement" style:family="paragraph"><style:paragraph-properties fo:text-align="center"/><style:text-properties fo:font-family="Noto Sans CJK KR" fo:font-size="20pt" fo:font-weight="bold" fo:color="#173B58"/></style:style>
 <style:style style:name="Body" style:family="paragraph"><style:paragraph-properties fo:margin-bottom="0.35cm"/><style:text-properties fo:font-family="Noto Sans CJK KR" fo:font-size="16pt" fo:color="#263B46"/></style:style>
 <style:style style:name="CardTitle" style:family="paragraph"><style:paragraph-properties fo:text-align="center"/><style:text-properties fo:font-family="Liberation Sans" fo:font-size="18pt" fo:font-weight="bold" fo:color="#0B315E"/></style:style>
 <style:style style:name="SectionTitle" style:family="paragraph"><style:text-properties fo:font-family="Noto Sans CJK KR" fo:font-size="19pt" fo:font-weight="bold" fo:color="#52766F"/></style:style>
 <style:style style:name="Callout" style:family="paragraph"><style:paragraph-properties fo:text-align="center"/><style:text-properties fo:font-family="Noto Sans CJK KR" fo:font-size="15pt" fo:font-weight="bold" fo:color="#8D6415"/></style:style>
 <style:style style:name="Equation" style:family="paragraph"><style:paragraph-properties fo:text-align="center"/><style:text-properties fo:font-family="Liberation Mono" fo:font-size="24pt" fo:font-weight="bold" fo:color="#092A54"/></style:style>
 <style:style style:name="Metric" style:family="paragraph"><style:paragraph-properties fo:text-align="center"/><style:text-properties fo:font-family="Liberation Sans" fo:font-size="44pt" fo:font-weight="bold" fo:color="#092A54"/></style:style>
 <style:style style:name="MetricGreen" style:family="paragraph"><style:paragraph-properties fo:text-align="center"/><style:text-properties fo:font-family="Liberation Sans" fo:font-size="38pt" fo:font-weight="bold" fo:color="#2E7563"/></style:style>
 <style:style style:name="MetricGold" style:family="paragraph"><style:paragraph-properties fo:text-align="center"/><style:text-properties fo:font-family="Liberation Sans" fo:font-size="38pt" fo:font-weight="bold" fo:color="#C28B1B"/></style:style>
 <style:style style:name="MetricRed" style:family="paragraph"><style:paragraph-properties fo:text-align="center"/><style:text-properties fo:font-family="Liberation Sans" fo:font-size="38pt" fo:font-weight="bold" fo:color="#A64B49"/></style:style>
 <style:style style:name="MetricLabel" style:family="paragraph"><style:paragraph-properties fo:text-align="center"/><style:text-properties fo:font-family="Liberation Sans" fo:font-size="16pt" fo:color="#52766F"/></style:style>
 <style:style style:name="Evidence" style:family="paragraph"><style:paragraph-properties fo:margin-bottom="0.45cm"/><style:text-properties fo:font-family="Liberation Mono" fo:font-size="17pt" fo:color="#173B58"/></style:style>
 <style:style style:name="Code" style:family="paragraph"><style:paragraph-properties fo:text-align="center"/><style:text-properties fo:font-family="Liberation Mono" fo:font-size="14pt" fo:color="#092A54"/></style:style>
 <style:style style:name="Closing" style:family="paragraph"><style:paragraph-properties fo:text-align="center"/><style:text-properties fo:font-family="Liberation Sans" fo:font-size="25pt" fo:font-weight="bold" fo:color="#092A54"/></style:style>
 <style:style style:name="Footer" style:family="paragraph"><style:text-properties fo:font-family="Liberation Sans" fo:font-size="8pt" fo:color="#7D8D8A"/></style:style>
 <style:presentation-page-layout style:name="AL1T0"><presentation:placeholder presentation:object="title" svg:x="1cm" svg:y="1cm" svg:width="31cm" svg:height="2cm"/></style:presentation-page-layout>
</office:automatic-styles>
<office:body><office:presentation>{"".join(slides)}</office:presentation></office:body>
</office:document-content>"""

meta = f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document-meta {NS}><office:meta/></office:document-meta>"""
settings = f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document-settings {NS}><office:settings/></office:document-settings>"""
manifest = """<?xml version="1.0" encoding="UTF-8"?>
<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0" manifest:version="1.2">
 <manifest:file-entry manifest:full-path="/" manifest:media-type="application/vnd.oasis.opendocument.presentation"/>
 <manifest:file-entry manifest:full-path="content.xml" manifest:media-type="text/xml"/>
 <manifest:file-entry manifest:full-path="styles.xml" manifest:media-type="text/xml"/>
 <manifest:file-entry manifest:full-path="meta.xml" manifest:media-type="text/xml"/>
 <manifest:file-entry manifest:full-path="settings.xml" manifest:media-type="text/xml"/>
 <manifest:file-entry manifest:full-path="Pictures/sage-logo.png" manifest:media-type="image/png"/>
</manifest:manifest>"""

with zipfile.ZipFile(OUT, "w") as z:
    z.writestr("mimetype", "application/vnd.oasis.opendocument.presentation",
               compress_type=zipfile.ZIP_STORED)
    z.writestr("content.xml", content)
    z.writestr("styles.xml", styles)
    z.writestr("meta.xml", meta)
    z.writestr("settings.xml", settings)
    z.writestr("META-INF/manifest.xml", manifest)
    z.write(LOGO, "Pictures/sage-logo.png")
print(OUT)
