import math
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QBrush, QPainterPath
from PySide6.QtCore import Qt, QRectF, QPointF

class IconEngine:
    """
    High-DPI Vector QIcon Factory for LedgerPro Desktop.
    Generates clean, professional UI icons via QPainter without external file dependencies or emojis.
    """
    @staticmethod
    def create_icon(icon_type, color_hex="#3B82F6", size=24):
        pixmap = QPixmap(size * 2, size * 2) # 2x for High DPI / Retina crispness
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        
        color = QColor(color_hex)
        pen = QPen(color, 1.8 * 2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        s = size * 2
        p = s * 0.15 # Padding
        w = s - 2 * p
        h = s - 2 * p
        
        t = icon_type.lower().replace(" ", "_")
        
        if t in ["dashboard", "home"]:
            # 4 rounded rect grid
            hw = w / 2 - s * 0.04
            hh = h / 2 - s * 0.04
            r = s * 0.06
            painter.setBrush(QBrush(color))
            painter.drawRoundedRect(QRectF(p, p, hw, hh), r, r)
            painter.drawRoundedRect(QRectF(p + hw + s * 0.08, p, hw, hh), r, r)
            painter.drawRoundedRect(QRectF(p, p + hh + s * 0.08, hw, hh), r, r)
            painter.drawRoundedRect(QRectF(p + hw + s * 0.08, p + hh + s * 0.08, hw, hh), r, r)
            
        elif t in ["customers", "customer", "contacts"]:
            # User head & shoulders
            painter.setBrush(QBrush(color))
            # Head
            head_r = s * 0.16
            painter.drawEllipse(QPointF(s / 2, p + head_r), head_r, head_r)
            # Body path
            path = QPainterPath()
            path.moveTo(p, s - p)
            path.quadTo(s / 2, p + head_r * 2.2, s - p, s - p)
            painter.drawPath(path)
            
        elif t in ["vendors", "vendor", "suppliers"]:
            # Building / Storefront
            painter.drawRect(QRectF(p + s * 0.05, p + s * 0.2, s * 0.7, s * 0.5))
            # Roof
            roof = QPainterPath()
            roof.moveTo(p, p + s * 0.2)
            roof.lineTo(s / 2, p)
            roof.lineTo(s - p, p + s * 0.2)
            painter.drawPath(roof)
            # Door
            painter.drawRect(QRectF(s / 2 - s * 0.08, p + s * 0.45, s * 0.16, s * 0.25))

        elif t in ["items", "item", "inventory", "products"]:
            # Box / Package 3D outline
            path = QPainterPath()
            cx, cy = s / 2, s / 2
            r_x, r_y = w / 2, h / 3
            # Top diamond
            path.moveTo(cx, cy - r_y)
            path.lineTo(cx + r_x, cy)
            path.lineTo(cx, cy + r_y)
            path.lineTo(cx - r_x, cy)
            path.closeSubpath()
            # Front sides
            path.moveTo(cx - r_x, cy)
            path.lineTo(cx - r_x, cy + r_y * 1.5)
            path.lineTo(cx, cy + r_y * 2.5)
            path.lineTo(cx + r_x, cy + r_y * 1.5)
            path.lineTo(cx + r_x, cy)
            path.moveTo(cx, cy + r_y)
            path.lineTo(cx, cy + r_y * 2.5)
            painter.drawPath(path)

        elif t in ["invoices", "invoice", "sales", "invoice_item"]:
            # Document with lines
            painter.drawRoundedRect(QRectF(p + s * 0.08, p, w - s * 0.16, h), s * 0.05, s * 0.05)
            line_y1 = p + h * 0.25
            line_y2 = p + h * 0.45
            line_y3 = p + h * 0.65
            x1 = p + s * 0.18
            x2 = s - p - s * 0.18
            painter.drawLine(QPointF(x1, line_y1), QPointF(x2, line_y1))
            painter.drawLine(QPointF(x1, line_y2), QPointF(x2, line_y2))
            painter.drawLine(QPointF(x1, line_y3), QPointF(x1 + (x2 - x1) * 0.6, line_y3))

        elif t in ["purchases", "purchases_(bills)", "bills", "bill"]:
            # Shopping cart / Receipt bag
            path = QPainterPath()
            path.moveTo(p + s * 0.1, p + s * 0.25)
            path.lineTo(s - p - s * 0.1, p + s * 0.25)
            path.lineTo(s - p - s * 0.18, s - p)
            path.lineTo(p + s * 0.18, s - p)
            path.closeSubpath()
            # Handle arc
            handle = QPainterPath()
            handle.moveTo(s / 2 - s * 0.12, p + s * 0.25)
            handle.cubicTo(s / 2 - s * 0.12, p + s * 0.05, s / 2 + s * 0.12, p + s * 0.05, s / 2 + s * 0.12, p + s * 0.25)
            painter.drawPath(path)
            painter.drawPath(handle)

        elif t in ["payments", "payment", "money", "cash"]:
            # Credit Card / Bank note
            painter.drawRoundedRect(QRectF(p, p + h * 0.15, w, h * 0.7), s * 0.06, s * 0.06)
            painter.setBrush(QBrush(color))
            painter.drawRect(QRectF(p, p + h * 0.32, w, h * 0.15))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(QRectF(p + w * 0.15, p + h * 0.58, w * 0.25, h * 0.12))

        elif t in ["stock", "stock_fifo", "warehouse"]:
            # Stacked layers
            for offset in [0, s * 0.22, s * 0.44]:
                path = QPainterPath()
                path.moveTo(s / 2, p + offset)
                path.lineTo(s - p, p + offset + s * 0.14)
                path.lineTo(s / 2, p + offset + s * 0.28)
                path.lineTo(p, p + offset + s * 0.14)
                path.closeSubpath()
                painter.drawPath(path)

        elif t in ["reports", "report", "analytics"]:
            # Bar chart with trend line
            b_w = w * 0.18
            # Bar 1
            painter.setBrush(QBrush(color))
            painter.drawRect(QRectF(p + w * 0.05, s - p - h * 0.35, b_w, h * 0.35))
            # Bar 2
            painter.drawRect(QRectF(p + w * 0.38, s - p - h * 0.65, b_w, h * 0.65))
            # Bar 3
            painter.drawRect(QRectF(p + w * 0.71, s - p - h * 0.9, b_w, h * 0.9))

        elif t in ["users", "user_management", "roles"]:
            # 2 People / Shield users
            head_r = s * 0.12
            painter.setBrush(QBrush(color))
            painter.drawEllipse(QPointF(p + w * 0.35, p + head_r + s * 0.05), head_r, head_r)
            path1 = QPainterPath()
            path1.moveTo(p, s - p)
            path1.quadTo(p + w * 0.35, p + head_r * 2.3, p + w * 0.7, s - p)
            painter.drawPath(path1)
            # User 2 (Background offset)
            painter.drawEllipse(QPointF(p + w * 0.7, p + head_r), head_r * 0.8, head_r * 0.8)

        elif t in ["audit", "audit_logs", "activity", "log"]:
            # Clipboard with checkmarks
            painter.drawRoundedRect(QRectF(p + s * 0.08, p + s * 0.1, w - s * 0.16, h - s * 0.1), s * 0.05, s * 0.05)
            # Clip top
            painter.setBrush(QBrush(color))
            painter.drawRoundedRect(QRectF(s / 2 - s * 0.12, p, s * 0.24, s * 0.15), s * 0.03, s * 0.03)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            # Check 1
            c1 = QPainterPath()
            c1.moveTo(p + s * 0.2, p + s * 0.35)
            c1.lineTo(p + s * 0.28, p + s * 0.43)
            c1.lineTo(p + s * 0.42, p + s * 0.28)
            painter.drawPath(c1)
            painter.drawLine(QPointF(p + s * 0.48, p + s * 0.36), QPointF(s - p - s * 0.15, p + s * 0.36))
            # Check 2
            c2 = QPainterPath()
            c2.moveTo(p + s * 0.2, p + s * 0.62)
            c2.lineTo(p + s * 0.28, p + s * 0.7)
            c2.lineTo(p + s * 0.42, p + s * 0.55)
            painter.drawPath(c2)
            painter.drawLine(QPointF(p + s * 0.48, p + s * 0.63), QPointF(s - p - s * 0.15, p + s * 0.63))

        elif t in ["settings", "setting", "gear", "config", "database_setup"]:
            # Gear / Cog
            cx, cy = s / 2, s / 2
            r_out = w * 0.45
            r_in = w * 0.3
            teeth = 8
            path = QPainterPath()
            for i in range(teeth * 2):
                angle = i * math.pi / teeth
                r = r_out if i % 2 == 0 else r_in
                x = cx + r * math.cos(angle)
                y = cy + r * math.sin(angle)
                if i == 0:
                    path.moveTo(x, y)
                else:
                    path.lineTo(x, y)
            path.closeSubpath()
            painter.drawPath(path)
            # Inner hole
            painter.drawEllipse(QPointF(cx, cy), w * 0.15, w * 0.15)

        elif t in ["about", "info", "help"]:
            # Circle with 'i'
            painter.drawEllipse(QPointF(s / 2, s / 2), w / 2, h / 2)
            painter.setBrush(QBrush(color))
            painter.drawEllipse(QPointF(s / 2, p + h * 0.28), s * 0.04, s * 0.04)
            painter.drawLine(QPointF(s / 2, p + h * 0.42), QPointF(s / 2, s - p - h * 0.2))

        elif t in ["logout", "exit", "close_app"]:
            # Door & Arrow
            painter.drawRect(QRectF(p, p, w * 0.45, h))
            # Arrow out
            arr = QPainterPath()
            arr.moveTo(p + w * 0.4, s / 2)
            arr.lineTo(s - p, s / 2)
            arr.lineTo(s - p - s * 0.12, s / 2 - s * 0.12)
            arr.moveTo(s - p, s / 2)
            arr.lineTo(s - p - s * 0.12, s / 2 + s * 0.12)
            painter.drawPath(arr)

        elif t in ["add", "plus", "create", "new"]:
            # Plus sign
            painter.drawLine(QPointF(s / 2, p + h * 0.15), QPointF(s / 2, s - p - h * 0.15))
            painter.drawLine(QPointF(p + w * 0.15, s / 2), QPointF(s - p - w * 0.15, s / 2))

        elif t in ["edit", "pencil", "modify"]:
            # Pencil angled
            path = QPainterPath()
            path.moveTo(s - p - s * 0.1, p + s * 0.1)
            path.lineTo(s - p, p + s * 0.2)
            path.lineTo(p + s * 0.2, s - p)
            path.lineTo(p, s - p)
            path.lineTo(p, s - p - s * 0.2)
            path.closeSubpath()
            painter.drawPath(path)

        elif t in ["delete", "trash", "remove"]:
            # Trash Bin
            painter.drawLine(QPointF(p + s * 0.1, p + s * 0.2), QPointF(s - p - s * 0.1, p + s * 0.2))
            painter.drawRoundedRect(QRectF(p + s * 0.18, p + s * 0.2, w - s * 0.36, h - s * 0.2), s * 0.04, s * 0.04)
            painter.drawLine(QPointF(s / 2 - s * 0.08, p + s * 0.35), QPointF(s / 2 - s * 0.08, s - p - s * 0.12))
            painter.drawLine(QPointF(s / 2 + s * 0.08, p + s * 0.35), QPointF(s / 2 + s * 0.08, s - p - s * 0.12))

        elif t in ["search", "find", "filter_search"]:
            # Magnifying Glass
            r_m = w * 0.3
            painter.drawEllipse(QPointF(p + r_m, p + r_m), r_m, r_m)
            painter.drawLine(QPointF(p + r_m * 1.7, p + r_m * 1.7), QPointF(s - p, s - p))

        elif t in ["print", "printer", "pdf_print", "pos_receipt"]:
            # Printer
            painter.drawRect(QRectF(p + s * 0.1, p + s * 0.28, w - s * 0.2, h * 0.4))
            # Paper top
            painter.drawRect(QRectF(p + s * 0.2, p, w - s * 0.4, s * 0.28))
            # Paper bottom
            painter.drawRect(QRectF(p + s * 0.2, p + s * 0.5, w - s * 0.4, s * 0.3))

        elif t in ["refresh", "reload", "update"]:
            # Circular arrow
            path = QPainterPath()
            path.arcTo(QRectF(p, p, w, h), 30, 300)
            painter.drawPath(path)
            # Arrow tip
            tip = QPainterPath()
            tip.moveTo(s - p - s * 0.05, s / 2 - s * 0.15)
            tip.lineTo(s - p - s * 0.05, s / 2 + s * 0.05)
            tip.lineTo(s - p - s * 0.25, s / 2 + s * 0.05)
            painter.drawPath(tip)

        elif t in ["save", "disk", "store"]:
            # Floppy disk
            painter.drawRoundedRect(QRectF(p, p, w, h), s * 0.04, s * 0.04)
            painter.drawRect(QRectF(p + w * 0.2, p, w * 0.6, h * 0.35))
            painter.drawRect(QRectF(p + w * 0.15, p + h * 0.5, w * 0.7, h * 0.4))

        elif t in ["lock", "security", "auth"]:
            # Padlock
            painter.drawRoundedRect(QRectF(p, p + h * 0.35, w, h * 0.65), s * 0.05, s * 0.05)
            shackle = QPainterPath()
            shackle.moveTo(p + w * 0.25, p + h * 0.35)
            shackle.lineTo(p + w * 0.25, p + h * 0.18)
            shackle.cubicTo(p + w * 0.25, p, s - p - w * 0.25, p, s - p - w * 0.25, p + h * 0.18)
            shackle.lineTo(s - p - w * 0.25, p + h * 0.35)
            painter.drawPath(shackle)

        else:
            # Generic bullet / dot fallback
            painter.setBrush(QBrush(color))
            painter.drawEllipse(QPointF(s / 2, s / 2), w / 3, h / 3)

        painter.end()
        return QIcon(pixmap)

def get_icon(name, color="#3B82F6", size=20):
    return IconEngine.create_icon(name, color_hex=color, size=size)
