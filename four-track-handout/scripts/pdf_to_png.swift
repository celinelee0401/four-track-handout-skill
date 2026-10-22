// Render every page of a PDF to PNG for visual QA (macOS PDFKit).
// usage: swift pdf_to_png.swift file.pdf OUT_DIR [scale]
import PDFKit
import AppKit
let a = CommandLine.arguments
guard a.count >= 3, let doc = PDFDocument(url: URL(fileURLWithPath: a[1])) else {
    print("usage: swift pdf_to_png.swift file.pdf OUT_DIR [scale]"); exit(1)
}
let scale = a.count > 3 ? CGFloat(Double(a[3])!) : 1.5
let out = URL(fileURLWithPath: a[2])
try? FileManager.default.createDirectory(at: out, withIntermediateDirectories: true)
let stem = URL(fileURLWithPath: a[1]).deletingPathExtension().lastPathComponent
for i in 0..<doc.pageCount {
    guard let page = doc.page(at: i) else { continue }
    let box = page.bounds(for: .mediaBox)
    let size = NSSize(width: box.width * scale, height: box.height * scale)
    let img = NSImage(size: size)
    img.lockFocus()
    NSColor.white.set(); NSRect(origin: .zero, size: size).fill()
    let ctx = NSGraphicsContext.current!.cgContext
    ctx.scaleBy(x: scale, y: scale)
    page.draw(with: .mediaBox, to: ctx)
    img.unlockFocus()
    let rep = NSBitmapImageRep(data: img.tiffRepresentation!)!
    let png = rep.representation(using: .png, properties: [:])!
    let file = out.appendingPathComponent("\(stem)-p\(i + 1).png")
    try! png.write(to: file)
    print(file.path)
}
