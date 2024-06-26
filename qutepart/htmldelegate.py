"""
htmldelegate --- QStyledItemDelegate delegate. Draws HTML
=========================================================
"""

from PySide2.QtWidgets import QApplication, QStyle, QStyledItemDelegate, \
                            QStyleOptionViewItem
from PySide2.QtGui import QAbstractTextDocumentLayout, \
                        QTextDocument, QPalette
from PySide2.QtCore import QSize

_HTML_ESCAPE_TABLE = \
{
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    " ": "&nbsp;",
    "\t": "&nbsp;&nbsp;&nbsp;&nbsp;",
}


def htmlEscape(text):
    """Replace special HTML symbols with escase sequences
    """
    return "".join(_HTML_ESCAPE_TABLE.get(c,c) for c in text)


class HTMLDelegate(QStyledItemDelegate):
    """QStyledItemDelegate implementation. Draws HTML

    http://stackoverflow.com/questions/1956542/how-to-make-item-view-render-rich-html-text-in-qt/1956781#1956781
    """

    def paint(self, painter, option, index):
        """QStyledItemDelegate.paint implementation
        """
        option.state &= ~QStyle.State_HasFocus  # never draw focus rect

        options = QStyleOptionViewItem(option)
        self.initStyleOption(options,index)

        style = QApplication.style() if options.widget is None else options.widget.style()

        doc = QTextDocument()
        doc.setDocumentMargin(1)
        doc.setHtml(options.text)
        if options.widget is not None:
            doc.setDefaultFont(options.widget.font())
        #  bad long (multiline) strings processing doc.setTextWidth(options.rect.width())

        options.text = ""
        style.drawControl(QStyle.CE_ItemViewItem, options, painter);

        ctx = QAbstractTextDocumentLayout.PaintContext()

        # Highlighting text if item is selected
        if option.state & QStyle.State_Selected:
            ctx.palette.setColor(QPalette.Text, option.palette.color(QPalette.Active, QPalette.HighlightedText))

        textRect = style.subElementRect(QStyle.SE_ItemViewItemText, options)
        painter.save()
        painter.translate(textRect.topLeft())
        """Original example contained line
            painter.setClipRect(textRect.translated(-textRect.topLeft()))
        but text is drawn clipped with it on kubuntu 12.04
        """
        doc.documentLayout().draw(painter, ctx)

        painter.restore()

    def sizeHint(self, option, index):
        """QStyledItemDelegate.sizeHint implementation
        """
        options = QStyleOptionViewItem(option)
        self.initStyleOption(options,index)

        doc = QTextDocument()
        doc.setDocumentMargin(1)
        #  bad long (multiline) strings processing doc.setTextWidth(options.rect.width())
        doc.setHtml(options.text)
        return QSize(int(doc.idealWidth()),
                     int(QStyledItemDelegate.sizeHint(self, option, index).height()))
