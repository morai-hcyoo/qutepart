"""Code editor component for PyQt and Pyside

Use Qutepart class as an API
"""

import os.path

from PyQt4.QtCore import QRect, Qt
from PyQt4.QtGui import QColor, QFont, QPainter, QPlainTextEdit, QTextEdit, QTextFormat, QWidget

from qutepart.syntax import SyntaxManager
from qutepart.highlighter import SyntaxHighlighter


class _LineNumberArea(QWidget):
    """Line number area widget
    """
    _LEFT_MARGIN = 3
    _RIGHT_MARGIN = 3
    
    def __init__(self, qpart):
        QWidget.__init__(self, qpart)
        self._qpart = qpart
    
    def sizeHint(self, ):
        """QWidget.sizeHint() implementation
        """
        return QSize(self.width(), 0)

    def paintEvent(self, event):
        """QWidget.paintEvent() implementation
        """
        painter = QPainter(self)
        painter.fillRect(event.rect(), Qt.lightGray)

        block = self._qpart.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self._qpart.blockBoundingGeometry(block).translated(self._qpart.contentOffset()).top())
        bottom = top + int(self._qpart.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(Qt.black)
                painter.drawText(0, top, self.width() - self._RIGHT_MARGIN, self._qpart.fontMetrics().height(),
                                 Qt.AlignRight, number)
            
            block = block.next()
            top = bottom
            bottom = top + int(self._qpart.blockBoundingRect(block).height())
            blockNumber += 1

    def width(self):
        """Desired width. Includes text and margins
        """
        digits = len(str(max(1, self._qpart.blockCount())))

        return self._LEFT_MARGIN + self._qpart.fontMetrics().width('9') * digits + self._RIGHT_MARGIN


class Qutepart(QPlainTextEdit):
    """Code editor component for PyQt and Pyside
    """
    
    _globalSyntaxManager = SyntaxManager()
    
    def __init__(self, *args):
        QPlainTextEdit.__init__(self, *args)
        
        self._highlighter = None
        
        self.setFont(QFont("Monospace"))

        self._lineNumberArea = _LineNumberArea(self)
        self._countCache = (-1, -1)

        self.blockCountChanged.connect(self._updateLineNumberAreaWidth)
        self.updateRequest.connect(self._updateLineNumberArea)
        self.cursorPositionChanged.connect(self._highlightCurrentLine)

        self._updateLineNumberAreaWidth(0)
        self._highlightCurrentLine()
    
    def detectSyntax(self, xmlFileName = None, mimeType = None, languageName = None, sourceFilePath = None):
        """Get syntax by one of parameters:
            * xmlFileName
            * mimeType
            * languageName
            * sourceFilePath
        First parameter in the list has biggest priority.
        Old syntax is always cleared, even if failed to detect new.
        
        Method returns True, if syntax is detected, and False otherwise
        """
        self.clearSyntax()
        
        syntax = self._globalSyntaxManager.getSyntax(SyntaxHighlighter.formatConverterFunction,
                                                     xmlFileName = xmlFileName,
                                                     mimeType = mimeType,
                                                     languageName = languageName,
                                                     sourceFilePath = sourceFilePath)

        if syntax is not None:
            self._highlighter = SyntaxHighlighter(syntax, self.document())

    def clearSyntax(self):
        """Clear syntax. Disables syntax highlighting
        
        This method might take long time, if document is big. Don't call it if you don't have to.
        """
        if self._highlighter is not None:
            self._highlighter.del_()
            self._highlighter = None
    
    def _updateLineNumberAreaWidth(self, newBlockCount):
        """Set line number are width according to current lines count
        """
        self.setViewportMargins(self._lineNumberArea.width(), 0, 0, 0)

    def _updateLineNumberArea(self, rect, dy):
        """Repaint line number area if necessary
        """
        # _countCache magic taken from Qt docs Code Editor Example
        if dy:
            self._lineNumberArea.scroll(0, dy)
        elif self._countCache[0] != self.blockCount() or \
             self._countCache[1] != self.textCursor().block().lineCount():
            self._lineNumberArea.update(0, rect.y(), self._lineNumberArea.width(), rect.height())
        self._countCache = (self.blockCount(), self.textCursor().block().lineCount())

        if rect.contains(self.viewport().rect()):
            self._updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        """QWidget.resizeEvent() implementation.
        Adjust line number area
        """
        QPlainTextEdit.resizeEvent(self, event)

        cr = self.contentsRect()
        self._lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self._lineNumberArea.width(), cr.height()))

    def _highlightCurrentLine(self):
        """Highlight current line
        """
        extraSelections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()

            lineColor = QColor(Qt.yellow).lighter(160)

            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        
        self.setExtraSelections(extraSelections)
