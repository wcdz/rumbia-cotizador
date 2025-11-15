import os
import json
import base64
from io import BytesIO
from typing import Dict, List, Optional
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Backend sin GUI para entornos de servidor
import pandas as pd


class ImageService:
    """Servicio para generar imágenes de cotizaciones"""
    
    def __init__(self):
        """Inicializa el servicio y crea la carpeta db si no existe"""
        self.output_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "db"
        )
        # Crear carpeta db si no existe
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generar_grafico_cotizacion(self, data: Dict, nombre_archivo: str = None, retornar_base64: bool = False) -> tuple[str, Optional[str]]:
        """
        Genera un gráfico de cotización con tabla resumen y lo guarda como JPEG
        
        Args:
            data: Diccionario con la estructura de cotización por colección
            nombre_archivo: Nombre opcional para el archivo (sin extensión)
            retornar_base64: Si True, también devuelve la imagen en base64
        
        Returns:
            Tupla (ruta_archivo, base64_string o None)
        """
        # Generar nombre de archivo si no se proporciona
        if nombre_archivo is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"cotizacion_{timestamp}"
        
        # Asegurar que no tiene extensión
        nombre_base = nombre_archivo.replace(".jpg", "").replace(".jpeg", "")
        archivo_salida = os.path.join(self.output_dir, f"{nombre_base}.jpg")
        
        # Crear figura con diseño vertical (gráfico arriba, tabla abajo)
        fig = plt.figure(figsize=(12, 10))
        
        # Usar gridspec para controlar mejor el layout
        # Ratio 2:1 entre gráfico y tabla
        gs = fig.add_gridspec(2, 1, height_ratios=[2, 1], hspace=0.3)
        
        # Subplot para el gráfico
        ax_plot = fig.add_subplot(gs[0])
        
        # Graficar cada periodo
        colores = ['#FF6B35', '#004E89', '#1B998B']  # Colores modernos
        for idx, cotizacion in enumerate(data["cotizaciones"]):
            periodo = cotizacion["periodo"]
            tabla_dev = json.loads(cotizacion["cotizacion"]["tabla_devolucion"])
            años = list(range(1, len(tabla_dev) + 1))
            
            # Seleccionar color de la lista (ciclar si hay más de 3)
            color = colores[idx % len(colores)]
            
            ax_plot.plot(
                años, 
                tabla_dev, 
                label=f"{periodo} años",
                marker='o',
                linewidth=2.5,
                markersize=6,
                color=color
            )
        
        # Configurar el gráfico
        ax_plot.set_xlabel("Años", fontsize=12, fontweight='bold')
        ax_plot.set_ylabel("Porcentaje de devolución", fontsize=12, fontweight='bold')
        
        # Título con la prima
        titulo = f"Evolución de devolución por periodo para una prima de S/ {data['prima']:.0f} mensual"
        ax_plot.set_title(titulo, fontsize=14, fontweight='bold', pad=20)
        ax_plot.legend(fontsize=10, loc='upper left')
        ax_plot.grid(True, alpha=0.3, linestyle='--')
        
        # Mejorar estética del gráfico
        ax_plot.spines['top'].set_visible(False)
        ax_plot.spines['right'].set_visible(False)
        
        # Subplot para la tabla
        ax_table = fig.add_subplot(gs[1])
        ax_table.axis("off")
        
        # Preparar datos de la tabla
        rows = []
        for cotizacion in data["cotizaciones"]:
            cot = cotizacion["cotizacion"]
            rows.append([
                cotizacion["periodo"],
                f"S/ {self._format_number(float(cot['aporte_total']))}",
                f"S/ {self._format_number(float(cot['devolucion_total']))}",
                f"S/ {self._format_number(float(cot['ganancia_total']))}",
                f"{cot['porcentaje_devolucion']}%"
            ])
        
        columns = ["Años de pago", "Aporte Total", "Devolución", "Ganancia total", "% devolución"]
        
        # Crear tabla
        table = ax_table.table(
            cellText=rows,
            colLabels=columns,
            loc="center",
            cellLoc="center",
            colWidths=[0.15, 0.22, 0.22, 0.22, 0.15]
        )
        
        # Estilizar tabla
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2.5)  # Aumentar altura de las celdas
        
        # Estilizar encabezados
        for i in range(len(columns)):
            cell = table[(0, i)]
            cell.set_facecolor('#004E89')
            cell.set_text_props(weight='bold', color='white')
        
        # Estilizar filas (alternar colores)
        for i in range(1, len(rows) + 1):
            for j in range(len(columns)):
                cell = table[(i, j)]
                if i % 2 == 0:
                    cell.set_facecolor('#F0F0F0')
                else:
                    cell.set_facecolor('#FFFFFF')
        
        # Ajustar layout y guardar
        plt.tight_layout()
        
        # Generar base64 si se solicita
        base64_string = None
        if retornar_base64:
            buffer = BytesIO()
            plt.savefig(buffer, format='jpeg', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            base64_string = base64.b64encode(buffer.read()).decode('utf-8')
            buffer.close()
        
        # Guardar archivo
        plt.savefig(archivo_salida, format='jpeg', dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        return archivo_salida, base64_string
    
    def _format_number(self, num: float) -> str:
        """
        Formatea un número con separador de miles
        
        Args:
            num: Número a formatear
        
        Returns:
            String formateado
        """
        return f"{num:,.2f}".replace(",", " ")
    
    def generar_grafico_desde_endpoint(self, prima: float, edad_actuarial: int, sexo: str, retornar_base64: bool = False) -> tuple[str, Optional[str]]:
        """
        Genera un gráfico llamando al servicio de cotizaciones
        
        Args:
            prima: Prima mensual
            edad_actuarial: Edad de contratación
            sexo: Sexo del cliente (M o F)
            retornar_base64: Si True, también devuelve la imagen en base64
        
        Returns:
            Tupla (ruta_archivo, base64_string o None)
        """
        from app.services.cotizacion_service import CotizacionService
        from app.schemas.cotizacion import CotizacionColeccionRequest
        
        # Crear request
        request = CotizacionColeccionRequest(
            prima=prima,
            edad_actuarial=edad_actuarial,
            sexo=sexo
        )
        
        # Obtener cotizaciones
        cotizacion_service = CotizacionService()
        response = cotizacion_service.crear_cotizacion_coleccion(request)
        
        # Convertir a diccionario
        data = response.model_dump()
        
        # Generar nombre de archivo con información relevante
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre = f"cotizacion_prima{int(prima)}_edad{edad_actuarial}_{sexo}_{timestamp}"
        
        # Generar gráfico
        return self.generar_grafico_cotizacion(data, nombre, retornar_base64=retornar_base64)
