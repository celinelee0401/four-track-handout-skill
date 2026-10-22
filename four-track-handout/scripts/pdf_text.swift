// Extract text from a PDF page range with macOS PDFKit.
// usage: swift pdf_text.swift file.pdf FIRST LAST
import PDFKit
let a = CommandLine.arguments
guard a.count >= 4, let doc = PDFDocument(url: URL(fileURLWithPath: a[1])) else {
    print("usage: swift pdf_text.swift file.pdf FIRST LAST"); exit(1)
}
let last = min(Int(a[3])!, doc.pageCount)
for i in (Int(a[2])! - 1)..<last {
    print("=== PAGE \(i + 1)")
    print(doc.page(at: i)?.string ?? "")
}
