import os
os.system("requirements.txt")
from matplotlib.patches import Patch
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import io
from PIL import Image as PILImage

# Configuración de la página
st.set_page_config(
    layout="wide", page_title="Análisis de Reclutamiento", page_icon="📊"
)

# Título de la aplicación
st.title("📊 Análisis de Datos de Reclutamiento")
# Carga de archivo
uploaded_file = st.file_uploader(
    "Sube tu archivo de datos (Excel o CSV)", type=["xlsx", "csv"]
)


# Función para descargar imágenes
def get_image_download_link(fig, filename, text):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
    buf.seek(0)
    img = PILImage.open(buf)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    return st.download_button(
        label=text, data=byte_im, file_name=filename, mime="image/png"
    )


if uploaded_file is not None:
    # Barra de progreso
    progress_bar = st.progress(0)
    status_text = st.empty()

    # Leer datos
    status_text.text("Leyendo datos...")
    if uploaded_file.name.endswith(".xlsx"):
        data = pd.read_excel(uploaded_file)
    else:
        data = pd.read_csv(uploaded_file)
    progress_bar.progress(10)

    # Procesamiento de datos
    status_text.text("Procesando datos...")
    data = data.replace("?", np.nan)

    # Eliminar duplicados, conservando el SEGUNDO registro (en lugar del primero)
    data = data.drop_duplicates(subset=["CURP"], keep="last")
    # Filtrar solo CURPs con 18+ caracteres (elimina toda la fila si no cumple)
    data = data[data["CURP"].str.len() >= 18]

    # Extraer columnas
    usuario = data["USUARIO"]
    region = data["REGION"]
    fechaNacimiento = pd.to_datetime(data["FECHA_NACIMIENTO"], errors="coerce")
    data["FECHA_NACIMIENTO"] = fechaNacimiento.dt.strftime("%d/%m/%Y")
    nacionalidad = data["NACIONALIDAD"]
    sexo = data["SEXO"]
    estadoCivil = data["ESTADO_CIVIL"]
    lenguaExtrajeraSelect = data["LENGUA_EXTRANJERA"]
    lenguaExtrajera = data["LENGUA_EXTRANJERA_2"]
    paisNacimiento = data["PAIS_NACIMIENTO"]
    estadoResidencia = data["ESTADO_RESIDENCIA"]
    escolaridad = data["ESCOLARIDAD"]
    estatura = data["ESTATURA"]
    peso = data["PESO"]
    masaCorporal = data["MASA_CORPORAL"]
    habilidadesTecnologicas = data["HABILIDADES_TECNOLOGICAS"]
    tallaPantalon = data["PANTALON_TALLA"]
    tallaCamisola = data["CAMISOLA_TALLA"]
    tallaChamarra = data["CHAMARRA_TALLA"]
    tallaCalzado = data["CALZADO_TALLA"]
    encuesta = data["P1_ENCUESTA"]
    comunidad = data["P2_ENCUESTA"]
    comunidadLGBT = data["P3_ENCUESTA"]
    seguridadAntecedentes = data["P4_ENCUESTA"]
    puestoAplicacion = data["P5_ENCUESTA"]
    fechaRegistro = pd.to_datetime(
        data["FECHA_REGISTRO"], format="%d/%m/%Y", errors="coerce"
    )
    data["FECHA_REGISTRO"] = fechaRegistro.dt.strftime(
        "%d/%m/%Y"
    )  # %I:%M:%S %p <- Para agregar hora, minuto y segundo

    # Obteniendo la fecha de nacimiento y comparando con la del CURP
    current_year = pd.Timestamp.now().year
    fechaNacimiento = pd.to_datetime(data["FECHA_NACIMIENTO"], errors="coerce")
    data["edad"] = current_year - fechaNacimiento.dt.year

    # Extrayendo información de fecha del CURP
    curp = data["CURP"]
    year_curp = (
        "19" + data["CURP"].str[4:5]
    )  # Asumiendo que son personas nacidas en el siglo XX
    month_curp = data["CURP"].str[6:7]  # Corregido: los meses están en posiciones 6-7
    day_curp = data["CURP"].str[8:9]  # Corregido: los días están en posiciones 8-9

    # Pasando el DataFrame data a un archivo excel, para que posteriormente se descargue el archivo filtrado
    data.to_excel("reclutamiento_data_filtrado.xlsx", index=False)

    # Construyendo la fecha del CURP
    fecha_curp = pd.to_datetime(
        day_curp + "/" + month_curp + "/" + year_curp,
        format="%d/%m/%Y",
        errors="coerce",  # Manejar casos donde la fecha no sea válida
    )
    print(fecha_curp)
    # Calculando edad basada en el CURP
    edad_curp = current_year - fecha_curp.dt.year

    # Comparando fechas y calculando edad final
    data["edad_final"] = np.where(
        fecha_curp.reset_index(drop=True) != fechaNacimiento.reset_index(drop=True),
        edad_curp.reset_index(drop=True),
        data["edad"],
    )

    progress_bar.progress(30)
    status_text.text("Generando visualizaciones...")

    # Función para mostrar gráficas en Streamlit con opción de descarga
    def show_plot(fig, title):
        # Mostrar imagen expandible
        with st.expander(f"Ver {title} en tamaño completo"):
            st.pyplot(fig, use_container_width=True)
            # Agregar botón de descarga
            get_image_download_link(
                fig, f"{title.replace(' ', '_')}.png", f"Descargar {title}"
            )
        plt.close(fig)

    # Crear pestañas para organizar las gráficas
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Distribuciones", "Análisis por Sexo", "Otros", "Análisis por estado"]
    )
    # -----------------------------------------------------------------------------------------------------------------------------------
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            # Clasificación de emails
            email_domains = usuario.str.extract(r"@(\w+)\.")[0]
            data["email_classification"] = email_domains.apply(
                lambda x: (
                    "gmail"
                    if "gmail" in str(x).lower()
                    else (
                        "outlook"
                        if "outlook" in str(x).lower()
                        else "hotmail" if "hotmail" in str(x).lower() else "otro"
                    )
                )
            )
            email_classification_counts = data["email_classification"].value_counts()

            # Crear figura con proyección 3D
            fig = plt.figure(figsize=(10, 15))
            ax = fig.add_subplot(111, projection="3d")

            # Configurar colores estilo Excel
            colors = [
                "#9b2247",
                "#002f2a",
                "#a57f2c",
                "#98989A",
            ]  # Colores típicos de Excel

            # Posiciones para las barras (con bases cuadradas)
            xpos = range(len(email_classification_counts))
            ypos = [0] * len(email_classification_counts)
            zpos = [0] * len(email_classification_counts)

            # Dimensiones de las barras (hacer bases cuadradas)
            dx = [0.6] * len(email_classification_counts)  # Ancho constante
            dy = [0.01] * len(
                email_classification_counts
            )  # Profundidad igual al ancho para bases cuadradas
            dz = email_classification_counts.values  # Altura variable

            # Crear gráfico de barras 3D con bases cuadradas
            bars = ax.bar3d(
                xpos, ypos, zpos, dx, dy, dz, color=colors, shade=True, alpha=0.8
            )

            # Agregar solo valores absolutos (eliminados los porcentajes)
            for i, (x, y, z) in enumerate(zip(xpos, ypos, dz)):
                ax.text(
                    x + dx[i] / 2,
                    y + dy[i] / 2,
                    z + max(dz) * 0.05,
                    f"{int(z)}",
                    ha="center",
                    va="bottom",
                    color="black",
                    fontsize=10,
                    fontweight="bold",
                    fontfamily="Noto Sans",
                    bbox=dict(facecolor="white", alpha=0.5, edgecolor="none"),
                )

            # Configuraciones adicionales estilo Excel
            ax.set_title("Distribución del email", fontweight="bold", fontsize=14, fontfamily="Noto Sans")
            ax.set_zlabel(
                "Cantidad de registros", labelpad=30, fontfamily="Noto Sans", fontsize=12
            )
            ax.set_ylabel("")
            ax.set_xticks(
                [i + dx[i] / 2 for i in xpos]
            )  # Centrar etiquetas en las barras
            ax.set_xticklabels(email_classification_counts.index, rotation=0, ha="center", fontsize=12, fontweight="bold", family="Noto Sans")
            ax.set_yticks([])

            # Hacer que las bases sean perfectamente cuadradas
            ax.set_box_aspect(
                [1, 0.6, 1]
            )  # Ajustar aspecto para visualizar bases cuadradas

            # Estilo de la cuadrícula más marcado
            ax.xaxis.pane.set_edgecolor("black")
            ax.yaxis.pane.set_edgecolor("black")
            ax.zaxis.pane.set_edgecolor("black")
            ax.xaxis.pane.set_alpha(1)
            ax.yaxis.pane.set_alpha(1)
            ax.zaxis.pane.set_alpha(1)
            ax.grid(True, linestyle="--", alpha=0.6, color="white")

            # Ajustar vista para mejor perspectiva 3D
            ax.view_init(elev=7, azim=-85)

            # Ajustar márgenes
            plt.tight_layout()

            show_plot(fig, "Distribución del email")
        # -----------------------------------------------------------------------------------------------------------------------------------
        # Gráfica de distribución por región
        with col2:
            # Obtener valores absolutos y porcentajes
            region_counts = region.value_counts()
            total = region_counts.sum()

            # Crear figura con proyección 3D
            fig = plt.figure(figsize=(10, 15))
            ax = fig.add_subplot(111, projection="3d")

            # Configurar colores estilo Excel
            colors = ["#1e5b4f", "#9b2247", "#a57f2c"]

            # Posiciones para las barras (con bases cuadradas)
            xpos = range(len(region_counts))
            ypos = [0] * len(region_counts)
            zpos = [0] * len(region_counts)

            # Dimensiones de las barras (hacer bases cuadradas)
            dx = [0.6] * len(region_counts)  # Ancho constante
            dy = [0.01] * len(
                region_counts
            )  # Profundidad igual al ancho para bases cuadradas
            dz = region_counts.values  # Altura variable

            # Crear gráfico de barras 3D con bases cuadradas
            bars = ax.bar3d(
                xpos, ypos, zpos, dx, dy, dz, color=colors, shade=True, alpha=0.8
            )

            # Agregar solo valores absolutos (eliminados los porcentajes)
            for i, (x, y, z) in enumerate(zip(xpos, ypos, dz)):
                ax.text(
                    x + dx[i] / 2,
                    y + dy[i] / 2,
                    z + max(dz) * 0.05,
                    f"{int(z)}",
                    ha="center",
                    va="bottom",
                    color="black",
                    fontsize=10,
                    fontweight="bold",
                    family="Noto Sans",
                    bbox=dict(facecolor="white", alpha=0.5, edgecolor="none"),
                )

            # Configuraciones adicionales estilo Excel
            ax.set_title(
                "Distribución por Región",
                fontweight="bold",
                fontsize=14,
                family="Noto Sans",
            )
            ax.set_zlabel(
                "Cantidad de registros", labelpad=30, family="Noto Sans", fontsize=12
            )
            ax.set_ylabel("")
            ax.set_xticks(
                [i + dx[i] / 2 for i in xpos]
            )  # Centrar etiquetas en las barras
            ax.set_xticklabels(
                region_counts.index,
                rotation=0,
                ha="center",
                fontsize=12,
                fontweight="bold",
                family="Noto Sans",
            )
            ax.set_yticks([])

            # Hacer que las bases sean perfectamente cuadradas
            ax.set_box_aspect(
                [1, 0.6, 1]
            )  # Ajustar aspecto para visualizar bases cuadradas

            # Estilo de la cuadrícula más marcado
            ax.xaxis.pane.set_edgecolor("black")
            ax.yaxis.pane.set_edgecolor("black")
            ax.zaxis.pane.set_edgecolor("black")
            ax.xaxis.pane.set_alpha(1)
            ax.yaxis.pane.set_alpha(1)
            ax.zaxis.pane.set_alpha(1)
            ax.grid(True, linestyle="--", alpha=0.6, color="white")

            # Ajustar vista para mejor perspectiva 3D
            ax.view_init(elev=7, azim=-85)

            # Ajustar márgenes
            plt.tight_layout()

            show_plot(fig, "Distribución por Región")

        # -----------------------------------------------------------------------------------------------------------------------------------
        # Gráfica de fecha de registro
        st.subheader("Distribución por Fecha de Registro")

        # Procesamiento de datos
        fecha_registro_counts = data["FECHA_REGISTRO"].value_counts(normalize=False)
        fecha_registro_counts = fecha_registro_counts.sort_index(
            key=lambda x: pd.to_datetime(x, format="%d/%m/%Y")
        )

        # Crear figura con proyección 3D
        fig = plt.figure(figsize=(25, 10))
        ax = fig.add_subplot(111, projection="3d")

        # Configurar colores (usando un solo color como en el original)
        color = "#1e5b4f"

        # Posiciones para las barras
        xpos = range(len(fecha_registro_counts))
        ypos = [0] * len(fecha_registro_counts)
        zpos = [0] * len(fecha_registro_counts)

        # Dimensiones de las barras (bases cuadradas)
        dx = [0.7] * len(fecha_registro_counts)  # Ancho constante
        dy = [0.4] * len(fecha_registro_counts)  # Profundidad igual al ancho
        dz = fecha_registro_counts.values  # Altura variable

        # Crear gráfico de barras 3D
        bars = ax.bar3d(
            xpos, ypos, zpos, dx, dy, dz, color=color, shade=True, alpha=0.8
        )

        # Agregar valores absolutos
        for i, (x, y, z) in enumerate(zip(xpos, ypos, dz)):
            ax.text(
                x + dx[i] / 2,
                y + dy[i] / 2,
                z + max(dz) * 0.05,
                f"{int(z)}",
                ha="center",
                va="bottom",
                color="black",
                fontsize=3,
                rotation=45,
                fontweight="bold",
                fontfamily="Noto Sans",
                bbox=dict(facecolor="white", alpha=0.5, edgecolor="none"),
            )

        # Configuraciones del gráfico
        ax.set_title(
            "Distribución por Fecha de Registro",
            fontweight="bold",
            fontsize=14,
            family="Noto Sans",
        )
        ax.set_zlabel(
            "Cantidad de Registros", labelpad=30, family="Noto Sans", fontsize=12
        )
        ax.set_ylabel("")
        ax.set_xticks([i + dx[i] / 2 for i in xpos])

        # Formatear fechas para mejor visualización
        formatted_dates = [
            pd.to_datetime(date).strftime("%d/%m/%y")
            for date in fecha_registro_counts.index
        ]
        ax.set_xticklabels(
            formatted_dates,
            rotation=45,
            ha="center",
            fontsize=6,
            fontweight="bold",
            family="Noto Sans",
        )
        ax.set_yticks([])

        # Ajustar aspecto para visualización 3D
        ax.set_box_aspect([1, 0.5, 1])

        # Estilo de los planos
        for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
            axis.pane.set_edgecolor("black")
            axis.pane.set_alpha(1)
            axis.grid(True, linestyle="--", alpha=0.6, color="white")

        # Vista optimizada para series temporales
        ax.view_init(elev=0, azim=-87)

        # Ajustar márgenes
        plt.tight_layout()

        show_plot(fig, "Distribución por Fecha de Registro")
        # -----------------------------------------------------------------------------------------------------------------------------------
        # Gráfica de distribución por edad en 3D
        st.subheader("Distribución por Edad")

        # Calcular límites dinámicos
        min_age = 18
        max_age = 50  # Limitar a 50 años

        # Agrupar edades menores a 18 y mayores a 50 en categorías separadas
        data["edad_agrupada"] = data["edad"].apply(
            lambda x: 17 if x < 18 else (x if x <= 50 else 51)
        )

        # Crear figura con proyección 3D
        fig = plt.figure(figsize=(20, 7))
        ax = fig.add_subplot(111, projection="3d")

        # Configurar color (usando el mismo color verde)
        color = "#611232"

        # Preparar datos para el histograma 3D
        age_counts = data["edad_agrupada"].value_counts().sort_index()
        ages = age_counts.index
        counts = age_counts.values

        # Posiciones para las barras (centradas en cada edad)
        xpos = [age - 0.5 for age in ages]  # Ajuste para centrar las barras
        ypos = [0] * len(ages)
        zpos = [0] * len(ages)

        # Dimensiones de las barras (bases cuadradas)
        dx = [0.5] * len(ages)  # Ancho constante (1 año)
        dy = [0.5] * len(ages)  # Profundidad igual al ancho
        dz = counts  # Altura variable

        # Crear gráfico de barras 3D
        bars = ax.bar3d(
            xpos, ypos, zpos, dx, dy, dz, color=color, shade=True, alpha=0.8
        )

        # Agregar valores absolutos
        for i, (x, y, z) in enumerate(zip(xpos, ypos, dz)):
            ax.text(
                x + dx[i] / 2,
                y + dy[i] / 2,
                z + max(dz) * 0.05,
                f"{int(z)}",
                ha="center",
                va="bottom",
                color="black",
                fontsize=4,
                fontweight="bold",
                rotation=0,
                fontfamily="Noto Sans",
                bbox=dict(facecolor="white", alpha=0.5, edgecolor="none"),
            )

        # Configuraciones del gráfico
        ax.set_title(
            "Distribución por Edad", fontweight="bold", fontsize=14, family="Noto Sans"
        )
        ax.set_zlabel(
            "Cantidad de Personas", labelpad=30, family="Noto Sans", fontsize=12
        )
        ax.set_ylabel("")
        ax.set_xlabel("", labelpad=10)

        # Ajustar ticks del eje X
        xticks = list(range(min_age, max_age + 1, 5)) + [51]
        ax.set_xticks([x - 0.5 for x in xticks])  # Ajustar posición de los ticks
        ax.set_xticklabels([str(x) if x != 51 else "51+" for x in xticks], rotation=0)

        ax.set_yticks([])

        # Ajustar aspecto para visualización 3D
        ax.set_box_aspect([2, 0.5, 1])  # Más ancho para acomodar todas las edades

        # Estilo de los planos
        for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
            axis.pane.set_edgecolor("black")
            axis.pane.set_alpha(1)
            axis.grid(True, linestyle="--", alpha=0.6, color="white")

        # Vista optimizada para histograma de edades
        ax.view_init(elev=0, azim=-89)

        # Ajustar márgenes
        plt.tight_layout()

        show_plot(fig, "Distribución por Edad")
        # -----------------------------------------------------------------------------------------------------------------------------------
        # Otras distribuciones
        col3, col4 = st.columns(2)
        with col3:
            # Nacionalidad
            nacionalidad_counts = nacionalidad.value_counts()
            total = nacionalidad_counts.sum()

            # Crear figura con proyección 3D
            fig = plt.figure(figsize=(8, 6))
            ax = fig.add_subplot(111, projection="3d")

            # Configurar colores (manteniendo los originales)
            colors = ["#9b2247", "#98989A"]  # Rosado y gris

            # Posiciones para las barras
            xpos = range(len(nacionalidad_counts))
            ypos = [0] * len(nacionalidad_counts)
            zpos = [0] * len(nacionalidad_counts)

            # Dimensiones de las barras (bases cuadradas)
            dx = [0.5] * len(nacionalidad_counts)  # Ancho constante
            dy = [0.5] * len(nacionalidad_counts)  # Profundidad igual al ancho
            dz = nacionalidad_counts.values  # Altura variable

            # Crear gráfico de barras 3D
            bars = ax.bar3d(
                xpos, ypos, zpos, dx, dy, dz, color=colors, shade=True, alpha=0.8
            )

            # Agregar valores absolutos
            for i, (x, y, z) in enumerate(zip(xpos, ypos, dz)):
                ax.text(
                    x + dx[i] / 2,
                    y + dy[i] / 2,
                    z + max(dz) * 0.05,
                    f"{int(z)}",
                    ha="center",
                    va="bottom",
                    color="black",
                    fontsize=10,
                    fontweight="bold",
                    fontfamily="Noto Sans",
                    bbox=dict(facecolor="white", alpha=0.5, edgecolor="none"),
                )

            # Configuraciones del gráfico
            ax.set_title(
                "Distribución por Nacionalidad",
                fontweight="bold",
                fontsize=14,
                family="Noto Sans",
            )
            ax.set_zlabel(
                "Número de registros", labelpad=30, family="Noto Sans", fontsize=12
            )
            ax.set_ylabel("")
            ax.set_xticks([i + dx[i] / 2 for i in xpos])
            ax.set_xticklabels(
                nacionalidad_counts.index,
                rotation=0,
                ha="center",
                fontsize=12,
                fontweight="bold",
                family="Noto Sans",
            )
            ax.set_yticks([])

            # Ajustar aspecto para visualización 3D
            ax.set_box_aspect([1, 0.5, 1])

            # Estilo de los planos
            for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
                axis.pane.set_edgecolor("black")
                axis.pane.set_alpha(1)
                axis.grid(True, linestyle="--", alpha=0.6, color="white")

            # Vista frontal con ligera perspectiva
            ax.view_init(elev=10, azim=-85)

            # Ajustar márgenes
            plt.tight_layout()

            show_plot(fig, "Distribución por Nacionalidad")
            # -----------------------------------------------------------------------------------------------------------------------------------
            # Sexo - Versión 3D
            with col4:
                # Calcular conteos absolutos
                absolute_counts = sexo.value_counts()

                # Crear figura con proyección 3D
                fig = plt.figure(figsize=(8, 6))
                ax = fig.add_subplot(111, projection="3d")

                # Configurar colores (manteniendo los originales)
                colors = ["#1e5b4f", "#611232"]  # Verde oscuro y vino

                # Posiciones para las barras
                xpos = range(len(absolute_counts))
                ypos = [0] * len(absolute_counts)
                zpos = [0] * len(absolute_counts)

                # Dimensiones de las barras (bases cuadradas)
                dx = [0.5] * len(absolute_counts)  # Ancho constante
                dy = [0.5] * len(absolute_counts)  # Profundidad igual al ancho
                dz = absolute_counts.values  # Altura variable

                # Crear gráfico de barras 3D (invertido como en el original)
                bars = ax.bar3d(
                    xpos, ypos, zpos, dx, dy, dz, color=colors, shade=True, alpha=0.8
                )

                # Agregar valores absolutos dentro de las barras (centrados verticalmente)
                for i, (x, y, z) in enumerate(zip(xpos, ypos, dz)):
                    ax.text(
                        x + dx[i] / 2,
                        y + dy[i] / 2,
                        z + max(dz) * 0.05,
                        f"{int(z)}",
                        ha="center",
                        va="bottom",
                        color="black",
                        fontsize=10,
                        fontweight="bold",
                        fontfamily="Noto Sans",
                        bbox=dict(facecolor="white", alpha=0.5, edgecolor="none"),
                    )

                # Configuraciones del gráfico
                ax.set_title(
                    "Distribución por Sexo",
                    fontweight="bold",
                    fontsize=14,
                    family="Noto Sans",
                )
                ax.set_zlabel("Cantidad", labelpad=30, family="Noto Sans", fontsize=12)
                ax.set_ylabel("")
                ax.set_xticks([i + dx[i] / 2 for i in xpos])
                ax.set_xticklabels(
                    absolute_counts.index,
                    rotation=0,
                    ha="center",
                    fontsize=12,
                    fontweight="bold",
                    family="Noto Sans",
                )
                ax.set_yticks([])

                # Invertir el orden como en el original
                ax.set_xlim(ax.get_xlim()[::-1])  # Invertir eje X

                # Ajustar aspecto para visualización 3D
                ax.set_box_aspect([1, 0.5, 1])

                # Estilo minimalista (similar al original)
                for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
                    axis.pane.set_edgecolor("none")
                    axis.pane.set_alpha(0.9)
                    axis.grid(True, linestyle="--", alpha=0.6, color="white")

                # Vista frontal con ligera perspectiva
                ax.view_init(elev=10, azim=-85)

                # Ajustar márgenes
                plt.tight_layout()

                show_plot(fig, "Distribución por Sexo")
        # -----------------------------------------------------------------------------------------------------------------------------------
        col5, col6 = st.columns(2)
        with col5:
            # Estado civil - Versión 3D
            estado_civil_counts = estadoCivil.value_counts()

            # Crear figura con proyección 3D
            fig = plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111, projection="3d")

            # Configurar colores (manteniendo la paleta original)
            colors = ["#9b2247", "#1e5b4f", "#e6d194", "#98989A"]

            # Posiciones para las barras
            xpos = range(len(estado_civil_counts))
            ypos = [0] * len(estado_civil_counts)
            zpos = [0] * len(estado_civil_counts)

            # Dimensiones de las barras (bases cuadradas)
            dx = [0.5] * len(estado_civil_counts)  # Ancho constante
            dy = [0.5] * len(estado_civil_counts)  # Profundidad igual al ancho
            dz = estado_civil_counts.values  # Altura variable

            # Crear gráfico de barras 3D
            bars = ax.bar3d(
                xpos, ypos, zpos, dx, dy, dz, color=colors, shade=True, alpha=0.8
            )

            # Agregar valores absolutos encima de cada barra
            for i, (x, y, z) in enumerate(zip(xpos, ypos, dz)):
                ax.text(
                    x + dx[i] / 2,
                    y + dy[i] / 2,
                    z + max(dz) * 0.05,
                    f"{int(z)}",
                    ha="center",
                    va="bottom",
                    color="black",
                    fontsize=10,
                    fontweight="bold",
                    fontfamily="Noto Sans",
                    bbox=dict(facecolor="white", alpha=0.5, edgecolor="none"),
                )

            # Configuraciones del gráfico
            ax.set_title(
                "Distribución por Estado Civil",
                fontweight="bold",
                fontsize=14,
                family="Noto Sans",
            )
            ax.set_zlabel("Cantidad", labelpad=30, family="Noto Sans", fontsize=12)
            ax.set_ylabel("")
            ax.set_xticks([i + dx[i] / 2 for i in xpos])
            ax.set_xticklabels(
                estado_civil_counts.index,
                rotation=0,
                ha="center",
                fontsize=9,
                fontweight="bold",
                family="Noto Sans",
            )
            ax.set_yticks([])

            # Ajustar aspecto para visualización 3D
            ax.set_box_aspect([1, 0.6, 1])

            # Estilo de los planos
            for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
                axis.pane.set_edgecolor("black")
                axis.pane.set_alpha(0.9)
                axis.grid(True, linestyle="--", alpha=0.6, color="white")

            # Vista optimizada para múltiples categorías
            ax.view_init(elev=10, azim=-85)

            # Ajustar márgenes para etiquetas rotadas
            plt.tight_layout()

            show_plot(fig, "Distribución por Estado Civil")
        # -----------------------------------------------------------------------------------------------------------------------------------
        with col6:
            # Segunda lengua
            # Obtener conteos absolutos
            abs_counts = lenguaExtrajeraSelect.value_counts()

            # Crear figura con proyección 3D
            fig = plt.figure(figsize=(8, 6))
            ax = fig.add_subplot(111, projection="3d")

            # Configurar colores (manteniendo los originales)
            colors = ["#1e5b4f", "#98989A"]  # Verde oscuro y gris

            # Posiciones para las barras
            xpos = range(len(abs_counts))
            ypos = [0] * len(abs_counts)
            zpos = [0] * len(abs_counts)

            # Dimensiones de las barras (bases cuadradas)
            dx = [0.5] * len(abs_counts)  # Ancho constante
            dy = [0.5] * len(abs_counts)  # Profundidad igual al ancho
            dz = abs_counts.values  # Altura variable

            # Crear gráfico de barras 3D
            bars = ax.bar3d(
                xpos, ypos, zpos, dx, dy, dz, color=colors, shade=True, alpha=0.8
            )

            # Agregar valores absolutos centrados en las barras
            for i, (x, y, z) in enumerate(zip(xpos, ypos, dz)):
                ax.text(
                    x + dx[i] / 2,
                    y + dy[i] / 2,
                    z + max(dz) * 0.05,
                    f"{int(z)}",
                    ha="center",
                    va="bottom",
                    color="black",
                    fontsize=10,
                    fontweight="bold",
                    fontfamily="Noto Sans",
                    bbox=dict(facecolor="white", alpha=0.5, edgecolor="none"),
                )

            # Configuraciones del gráfico
            ax.set_title(
                "Distribución por Segunda Lengua",
                fontweight="bold",
                fontsize=14,
                family="Noto Sans",
            )
            ax.set_zlabel(
                "Cantidad de personas", labelpad=30, family="Noto Sans", fontsize=12
            )
            ax.set_ylabel("")
            ax.set_xticks([i + dx[i] / 2 for i in xpos])
            ax.set_xticklabels(
                abs_counts.index,
                rotation=0,
                ha="center",
                fontsize=9,
                fontweight="bold",
                family="Noto Sans",
            )
            ax.set_yticks([])

            # Ajustar aspecto para visualización 3D
            ax.set_box_aspect([1, 0.5, 1])

            # Estilo de los planos (más limpio)
            for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
                axis.pane.set_edgecolor("none")
                axis.pane.set_alpha(0.9)
                axis.grid(True, linestyle="--", alpha=0.6, color="white")

            # Vista frontal con ligera perspectiva
            ax.view_init(elev=10, azim=-85)

            # Ajustar márgenes
            plt.tight_layout()

            show_plot(fig, "Distribución por Segunda Lengua")
        # -----------------------------------------------------------------------------------------------------------------------------------
        col7, col8 = st.columns(2)
        with col7:
            # Clasificar lengua extranjera (función se mantiene igual)
            def classify_lengua(value):
                value = str(value).lower()
                if re.search(r"ing", value):
                    return "Inglés"
                elif re.search(r"nahuatl", value):
                    return "Náhuatl"
                elif re.search(r"zapoteco", value):
                    return "Zapoteco"
                elif re.search(r"Amuzgo", value):
                    return "Lengua indigena"
                elif re.search(r"Amuzga", value):
                    return "Lengua indigena"
                elif re.search(r"chol", value):
                    return "Lengua indigena"
                elif re.search(r"chontal", value):
                    return "Lengua indigena"
                else:
                    return "Otro o ninguno"

            # Procesamiento de datos
            lenguaExtrajera_classified = lenguaExtrajera.apply(classify_lengua)
            counts = lenguaExtrajera_classified.value_counts()

            # Crear figura con proyección 3D
            fig = plt.figure(figsize=(8, 6))
            ax = fig.add_subplot(111, projection="3d")

            # Configurar colores (manteniendo la paleta original)
            colors = ["#1e5b4f", "#9b2247", "#a57f2c", "#98989A", "#002f2a"]

            # Posiciones para las barras
            xpos = range(len(counts))
            ypos = [0] * len(counts)
            zpos = [0] * len(counts)

            # Dimensiones de las barras (bases cuadradas)
            dx = [0.8] * len(counts)  # Ancho constante
            dy = [0.8] * len(counts)  # Profundidad igual al ancho
            dz = counts.values  # Altura variable

            # Crear gráfico de barras 3D
            bars = ax.bar3d(
                xpos, ypos, zpos, dx, dy, dz, color=colors, shade=True, alpha=0.8
            )

            # Agregar valores absolutos encima de cada barra
            for i, (x, y, z) in enumerate(zip(xpos, ypos, dz)):
                ax.text(
                    x + dx[i] / 2,
                    y + dy[i] / 2,
                    z + max(dz) * 0.05,
                    f"{int(z)}",
                    ha="center",
                    va="bottom",
                    color="black",
                    fontsize=10,
                    fontweight="bold",
                    fontfamily="Noto Sans",
                    bbox=dict(facecolor="white", alpha=0.5, edgecolor="none"),
                )

            # Configuraciones del gráfico
            ax.set_title(
                "Distribución por Lengua Extranjera",
                fontweight="bold",
                fontsize=14,
                family="Noto Sans",
            )
            ax.set_zlabel("Cantidad", labelpad=30, family="Noto Sans", fontsize=12)
            ax.set_ylabel("")
            ax.set_xticks([i + dx[i] / 2 for i in xpos])
            ax.set_xticklabels(
                counts.index,
                rotation=0,
                ha="center",
                fontsize=5,
                fontweight="bold",
                family="Noto Sans",
                wrap=True,
            )
            ax.set_yticks([])

            # Ajustar aspecto para mejor visualización
            ax.set_box_aspect([1, 0.5, 1])

            # Estilo de los planos
            for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
                axis.pane.set_edgecolor("black")
                axis.pane.set_alpha(0.9)
                axis.grid(True, linestyle="--", alpha=0.6, color="white")

            # Vista optimizada para múltiples categorías
            ax.view_init(elev=10, azim=-85)

            # Ajustar márgenes para etiquetas rotadas
            plt.tight_layout()

            show_plot(fig, "Distribución por Lengua Extranjera")
    # -----------------------------------------------------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------------------------------
    with tab2:
        st.header("Análisis por Sexo")

        # Preparar datos
        region_gender = pd.concat([region, sexo], axis=1)
        region_gender.columns = ["Región", "Sexo"]
        absolute_counts = (
            region_gender.groupby("Sexo")["Región"].value_counts().unstack(fill_value=0)
        )

        # Crear figura
        fig, ax = plt.subplots(figsize=(10, 6))

        # Configurar estilo 3D simulado
        ax.set_facecolor("#f5f5f5")  # Fondo gris claro como Excel
        colors = ["#1e5b4f", "#9b2247", "#e6d194", "#002f2a", "#9b2247"]

        # Crear efecto 3D para barras apiladas
        for i, (sexo_cat, row) in enumerate(absolute_counts.iloc[::-1].iterrows()):
            bottom = 0
            for j, (region_cat, value) in enumerate(row.items()):
                if value > 0:
                    # Dibujar barra principal
                    bar = ax.bar(
                        i,
                        value,
                        width=0.6,
                        bottom=bottom,
                        color=colors[j % len(colors)],
                        alpha=0.8,
                        edgecolor="white",
                        linewidth=0.5,
                    )

                    # Efecto 3D - lado derecho
                    ax.plot(
                        [i + 0.3, i + 0.3],
                        [bottom, bottom + value],
                        color=colors[j % len(colors)],
                        alpha=0.5,
                        linewidth=2,
                    )

                    # Efecto 3D - parte superior
                    ax.plot(
                        [i - 0.3, i + 0.3],
                        [bottom + value, bottom + value],
                        color=colors[j % len(colors)],
                        alpha=0.3,
                        linewidth=2,
                    )

                    # Etiqueta con valor
                    ax.text(
                        i,
                        bottom + value / 2,
                        f"{int(value)}",
                        ha="center",
                        va="center",
                        color="black",
                        fontsize=8,
                        fontweight="bold",
                        fontfamily="Noto Sans",
                        )

                    bottom += value

        # Configuración del gráfico
        ax.set_title(
            "Distribución de Regiones por Sexo",
            fontweight="bold",
            fontsize=14,
            fontfamily="Noto Sans",
        )
        ax.set_ylabel("Cantidad", labelpad=30, fontfamily="Noto Sans", fontsize=12)
        ax.set_xlabel("")
        ax.set_xticks(range(len(absolute_counts)))
        ax.set_xticklabels(absolute_counts.index[::-1], rotation=0, ha="center", fontsize=12, fontweight="bold", family="Noto Sans")
        ax.grid(axis="y", linestyle="--", alpha=0.7)

        # Leyenda mejorada
        patches = [
            Patch(color=colors[i], label=col)
            for i, col in enumerate(absolute_counts.columns)
        ]
        ax.legend(
            handles=patches,
            title="Región",
            loc="upper right",
            bbox_to_anchor=(1.15, 1),
            framealpha=0.9
        )

        # Efecto de sombra para simular profundidad
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.spines["bottom"].set_visible(True)
        ax.spines["bottom"].set_color("#d0d0d0")

        plt.tight_layout()
        show_plot(fig, "Distribución de Regiones por Sexo")
        # -----------------------------------------------------------------------------------------------------------------------------------
        # Escolaridad por sexo
        st.subheader("Distribución de Escolaridad por Sexo")

        # Preparar datos
        escolaridad_gender = pd.concat([escolaridad, sexo], axis=1)
        escolaridad_gender.columns = ["Escolaridad", "Sexo"]

        # Calcular frecuencias absolutas
        abs_counts = (
            escolaridad_gender.groupby("Sexo")["Escolaridad"].value_counts().unstack()
        )

        # Ordenar columnas
        sorted_columns = abs_counts.sum().sort_values(ascending=False).index
        abs_counts = abs_counts[sorted_columns]

        # Crear figura
        fig, ax = plt.subplots(figsize=(12, 7))
        ax.set_facecolor("#f5f5f5")  # Fondo gris claro estilo Excel
        colors = ["#98989A", "#611232", "#1e5b4f", "#e6d194", "#161a1d"]

        # Dibujar barras con efecto 3D
        for i, (sexo_cat, row) in enumerate(abs_counts.iterrows()):
            bottom = 0
            for j, (escolaridad_cat, value) in enumerate(row.items()):
                if value > 0:
                    # Barra principal
                    bar = ax.bar(
                    i,
                    value,
                    width=0.6,
                    bottom=bottom,
                    color=colors[j % len(colors)],
                    alpha=0.8,
                    edgecolor="white",
                    linewidth=0.5,
                    )

                    # Efecto 3D - lado derecho
                    ax.plot(
                    [i + 0.3, i + 0.3],
                    [bottom, bottom + value],
                    color=colors[j % len(colors)],
                    alpha=0.5,
                    linewidth=2,
                    )

                    # Efecto 3D - parte superior
                    ax.plot(
                    [i - 0.3, i + 0.3],
                    [bottom + value, bottom + value],
                    color=colors[j % len(colors)],
                    alpha=0.3,
                    linewidth=2,
                    )

                    # Etiqueta con valor absoluto
                    ax.text(
                    i,
                    bottom + value / 2,
                    f"{int(value)}",
                    ha="center",
                    va="center",
                    color="black",
                    fontsize=8,
                    fontweight="bold",
                    fontfamily="Noto Sans"
                    )

                    bottom += value

        # Configuración del gráfico
        ax.set_title("Distribución de Escolaridad por Sexo", fontweight="bold", fontsize=14, fontfamily="Noto Sans")
        ax.set_ylabel("Cantidad", labelpad=30, fontfamily="Noto Sans", fontsize=12)
        ax.set_xlabel("")
        ax.set_xticks(range(len(abs_counts)))
        ax.set_xticklabels(abs_counts.index, rotation=0, ha="center", fontsize=12, fontweight="bold", family="Noto Sans")
        ax.invert_xaxis()
        ax.grid(axis="y", linestyle="--", alpha=0.7)

        # Leyenda mejorada
        patches = [
            Patch(color=colors[i], label=col)
            for i, col in enumerate(abs_counts.columns)
        ]
        ax.legend(
            handles=patches,
            title="Escolaridad",
            loc="center left",
            bbox_to_anchor=(1, 0.5),
            framealpha=0.9
        )

        # Efectos de profundidad
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.spines["bottom"].set_visible(True)
        ax.spines["bottom"].set_color("#d0d0d0")
        plt.tight_layout()
        show_plot(fig, "Distribución de Escolaridad por Sexo")
        # -----------------------------------------------------------------------------------------------------------------------------------------
        # Haciendo el histograma por Masa Corporal
        st.subheader("Distribución de Masa Corporal por Sexo")

        # Masa corporal por sexo - Crear histogramas separados por sexo
        for gender, color in zip(["MUJER", "HOMBRE"], ["#9b2247", "#1e5b4f"]):
            if gender in sexo.unique():
                fig, ax = plt.subplots(figsize=(10, 6))
                data_gender = masaCorporal[sexo == gender].dropna()

            # Crear histograma
            n, bins, patches = ax.hist(
                data_gender,
                bins=15,  # Número de bins ajustable
                color=color,
                alpha=0.7,
                edgecolor="white",
            )

            # Añadir etiquetas con valores absolutos
            for i in range(len(n)):
                ax.text(
                    bins[i] + (bins[i + 1] - bins[i]) / 2,
                    n[i],
                    f"{int(n[i])}",  # Convertir a entero para quitar el punto decimal
                    ha="center",
                    va="bottom",
                    fontsize=8,
                    fontweight="bold",
                    fontfamily="Noto Sans",
                    bbox=dict(facecolor="white", alpha=0.5, edgecolor="none")
                )

            ax.set_title(f"Distribución de Masa Corporal ({gender})", fontweight="bold", fontsize=14, fontfamily="Noto Sans")
            ax.set_ylabel("Cantidad de Personas", labelpad=30, fontfamily="Noto Sans", fontsize=12)
            ax.set_xlabel("")

            ax.grid(axis="y", linestyle="--", alpha=0.6)
            plt.tight_layout()
            show_plot(fig, f"Distribución de Masa Corporal ({gender})")
        # ----------------------------------------------------------------------------------------------------------------------------------------------------
        # Relación entre sexo y puesto de aplicación
        st.subheader("Relación entre Sexo y Puesto de Aplicación")

        # Agrupar datos por sexo y puesto de aplicación
        sexo_puesto_counts = (
            pd.concat([sexo, puestoAplicacion], axis=1)
            .groupby(["SEXO", "P5_ENCUESTA"])
            .size()
            .unstack(fill_value=0)
        )

        # Crear la gráfica
        fig, ax = plt.subplots(figsize=(10, 6))
        bar_width = 0.4
        x = np.arange(len(sexo_puesto_counts.columns))

        # Barras para mujeres
        ax.bar(
            x - bar_width / 2,
            sexo_puesto_counts.loc["MUJER"],
            width=bar_width,
            color="#9b2247",
            label="Mujeres",
            alpha=0.8,
            edgecolor="white",
        )

        # Barras para hombres
        ax.bar(
            x + bar_width / 2,
            sexo_puesto_counts.loc["HOMBRE"],
            width=bar_width,
            color="#1e5b4f",
            label="Hombres",
            alpha=0.8,
            edgecolor="white",
        )

        # Añadir valores absolutos sobre las barras
        for i, puesto in enumerate(sexo_puesto_counts.columns):
            # Mujeres
            ax.text(
                x[i] - bar_width / 2,
                sexo_puesto_counts.loc["MUJER", puesto] + 1,
                f"{sexo_puesto_counts.loc['MUJER', puesto]}",
                ha="center",
                va="bottom",
                fontsize=8,
            )
            # Hombres
            ax.text(
                x[i] + bar_width / 2,
                sexo_puesto_counts.loc["HOMBRE", puesto] + 1,
                f"{sexo_puesto_counts.loc['HOMBRE', puesto]}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

        # Configurar el gráfico
        ax.set_title("Relación entre Sexo y Puesto de Aplicación", fontweight="bold", fontsize=14, fontfamily="Noto Sans")
        ax.set_ylabel("Cantidad", labelpad=30, fontfamily="Noto Sans", fontsize=12)
        ax.set_xlabel("")
        ax.set_xticks(x)
        ax.set_xticklabels(
            [
            col if len(col) <= 12 else "\n".join(re.findall(r'.{1,12}(?:\s+|$)', col))
            for col in sexo_puesto_counts.columns
            ],
            rotation=0,
            va="top",
            ha="center",
            fontsize=7,
            fontweight="bold",
            fontfamily="Noto Sans",
            wrap=True,
        )
        ax.legend(title="Sexo")
        ax.grid(axis="y", linestyle="--", alpha=0.6)

        # Mostrar el gráfico
        show_plot(fig, "Relación entre Sexo y Puesto de Aplicación")
        # ----------------------------------------------------------------------------------------------------------------------------------------------------
        # Gráfica de Estado civil por sexo
        # Relación entre sexo y estado civil
        st.subheader("Relación entre Sexo y Estado Civil")

        # Agrupar datos por sexo y estado civil
        sexo_estado_civil_counts = (
            pd.concat([sexo, estadoCivil], axis=1)
            .groupby(["SEXO", "ESTADO_CIVIL"])
            .size()
            .unstack(fill_value=0)
        )

        # Crear la gráfica
        fig, ax = plt.subplots(figsize=(10, 6))
        bar_width = 0.4
        x = np.arange(len(sexo_estado_civil_counts.columns))

        # Barras para mujeres
        ax.bar(
            x - bar_width / 2,
            sexo_estado_civil_counts.loc["MUJER"],
            width=bar_width,
            color="#9b2247",
            label="Mujeres",
            alpha=0.8,
            edgecolor="white"
        )

        # Barras para hombres
        ax.bar(
            x + bar_width / 2,
            sexo_estado_civil_counts.loc["HOMBRE"],
            width=bar_width,
            color="#1e5b4f",
            alpha=0.8,
            edgecolor="white",
            label="Hombres",
        )

        # Añadir valores absolutos sobre las barras
        for i, estado in enumerate(sexo_estado_civil_counts.columns):
            # Mujeres
            ax.text(
                x[i] - bar_width / 2,
                sexo_estado_civil_counts.loc["MUJER", estado] + 1,
                f"{sexo_estado_civil_counts.loc['MUJER', estado]}",
                ha="center",
                va="bottom",
                fontsize=8,
            )
            # Hombres
            ax.text(
                x[i] + bar_width / 2,
                sexo_estado_civil_counts.loc["HOMBRE", estado] + 1,
                f"{sexo_estado_civil_counts.loc['HOMBRE', estado]}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

        # Configurar el gráfico
        ax.set_title("Relación entre Sexo y Estado Civil", fontweight="bold", fontsize=14, fontfamily="Noto Sans")
        ax.set_ylabel("Cantidad", labelpad=30, fontfamily="Noto Sans", fontsize=12)
        ax.set_xlabel("")
        ax.set_xticks(x)
        ax.set_xticklabels(sexo_estado_civil_counts.columns, rotation=0, ha="center", fontsize=10, fontweight="bold", fontfamily="Noto Sans")
        ax.legend(title="Sexo")
        ax.grid(axis="y", linestyle="--", alpha=0.6)

        # Mostrar el gráfico
        show_plot(fig, "Relación entre Sexo y Estado Civil")
        # ----------------------------------------------------------------------------------------------------------------------------------------------------

    with tab3:
        st.header("Otras Distribuciones")

        # Habilidades tecnológicas en 3D
        st.subheader("Habilidades Tecnológicas")

        # Clasificación de habilidades (se mantiene igual)
        def classify_habilidades(value):
            value = str(value).lower()
            if re.search(r"si-100%", value):
                return "100%"
            elif re.search(r"si-90%", value):
                return "90%"
            elif re.search(r"si-80%", value):
                return "80%"
            elif re.search(r"si-70%", value):
                return "70%"
            elif re.search(r"si-60%", value):
                return "60%"
            elif re.search(r"si-50%", value):
                return "50%"
            elif re.search(r"si-40%", value):
                return ">40%"
            elif re.search(r"si-30%", value):
                return ">40%"
            elif re.search(r"si-20%", value):
                return ">40%"
            elif re.search(r"si-10%", value):
                return ">40%"
            elif re.search(r"si-0%", value):
                return ">40%"
            else:
                return "NO"

        # Procesar datos
        habilidadesTecnologicas_classified = habilidadesTecnologicas.apply(
            classify_habilidades
        )
        counts = habilidadesTecnologicas_classified.value_counts()

        # Ordenar categorías (de mayor a menor habilidad)
        ordered_categories = ["100%", "90%", "80%", "70%", "60%", "50%", ">40%", "NO"]
        counts = counts.reindex(ordered_categories, fill_value=0)

        # Crear figura 3D
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection="3d")

        # Configurar colores (manteniendo la paleta original)
        colors = [
            "#98989A",
            "#9b2247",
            "#002f2a",
            "#a57f2c",
            "#161a1d",
            "#611232",
            "#1e5b4f",
            "#e6d194",
        ]

        # Posiciones y dimensiones de las barras
        xpos = range(len(counts))
        ypos = [0] * len(counts)
        zpos = [0] * len(counts)
        dx = [0.8] * len(counts)  # Ancho constante
        dy = [0.8] * len(counts)  # Profundidad (bases cuadradas)
        dz = counts.values  # Altura variable

        # Crear barras 3D
        bars = ax.bar3d(
            xpos, ypos, zpos, dx, dy, dz, color=colors, shade=True, alpha=0.8
        )

        # Añadir etiquetas de valores absolutos ENCIMA de cada barra
        for i, (x, y, z) in enumerate(zip(xpos, ypos, dz)):
                ax.text(
                    x + dx[i] / 2,
                    y + dy[i] / 2,
                    z + max(dz) * 0.05,
                    f"{int(z)}",
                    ha="center",
                    va="bottom",
                    color="black",
                    fontsize=10,
                    fontweight="bold",
                    fontfamily="Noto Sans",
                    bbox=dict(facecolor="white", alpha=0.5, edgecolor="none"),
                )

        # Configuración del gráfico
        ax.set_title("Distribución de Habilidades Tecnológicas", fontweight="bold", fontsize=14, fontfamily="Noto Sans")
        ax.set_zlabel("Cantidad", labelpad=30, fontfamily="Noto Sans", fontsize=12)
        ax.set_ylabel("")
        ax.set_xlabel("")
        ax.set_xticks([i + 0.4 for i in xpos])
        ax.set_xticklabels(counts.index, rotation=0, ha="center", fontsize=10, fontweight="bold", family="Noto Sans")
        ax.set_yticks([])

        # Ajustar aspecto para visualización 3D
        ax.set_box_aspect([1, 0.6, 1])

        # Estilo de los planos
        for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
            axis.pane.set_edgecolor("black")
            axis.pane.set_alpha(0.8)
            axis.grid(True, linestyle="--", alpha=0.6, color="white")

        # Vista optimizada
        ax.view_init(elev=10, azim=-85)

        plt.tight_layout()
        show_plot(fig, "Habilidades Tecnológicas")
        # ----------------------------------------------------------------------------------------------------------------------------------------------------

        # Estado de residencia
        st.subheader("Estado de Residencia - Top 10")

        # Obtener los 10 estados con más residentes
        estadoResidencia_counts = estadoResidencia.value_counts(normalize=False)
        top_10_estadoResidencia = estadoResidencia_counts[:10]

        # Crear figura 3D
        fig = plt.figure(figsize=(20, 10))
        ax = fig.add_subplot(111, projection="3d")

        # Configurar posiciones y dimensiones de las barras
        xpos = range(len(top_10_estadoResidencia))
        ypos = [0] * len(top_10_estadoResidencia)
        zpos = [0] * len(top_10_estadoResidencia)
        dx = [0.8] * len(top_10_estadoResidencia)  # Ancho constante
        dy = [0.5] * len(top_10_estadoResidencia)  # Profundidad (bases cuadradas)
        dz = top_10_estadoResidencia.values  # Altura variable

        # Crear barras 3D con color verde similar al original (#1e5b4f)
        bars = ax.bar3d(
            xpos, ypos, zpos, dx, dy, dz, color="#a57f2c", shade=True, alpha=0.8
        )

        # Añadir etiquetas de valores absolutos ENCIMA de cada barra
        for i, (x, y, z) in enumerate(zip(xpos, ypos, dz)):
                ax.text(
                    x + dx[i] / 2,
                    y + dy[i] / 2,
                    z + max(dz) * 0.05,
                    f"{int(z)}",
                    ha="center",
                    va="bottom",
                    color="black",
                    fontsize=10,
                    fontweight="bold",
                    fontfamily="Noto Sans",
                    bbox=dict(facecolor="white", alpha=0.5, edgecolor="none"),
                )

        # Configuración del gráfico
        ax.set_title(
            "Distribución por Estado de Residencia - Top 10",fontweight="bold", fontsize=14, fontfamily="Noto Sans"
        )
        ax.set_zlabel("Cantidad", labelpad=30, fontfamily="Noto Sans", fontsize=12)
        ax.set_ylabel("")
        ax.set_xlabel("")
        ax.set_xticks([i + 0.4 for i in xpos])
        ax.set_xticklabels( [
            col if len(col) <= 12 else "\n".join(re.findall(r'.{1,12}(?:\s+|$)', col))
            for col in top_10_estadoResidencia.index
            ], rotation=0, ha="center", fontsize=7, fontweight="bold", family="Noto Sans")
        ax.set_yticks([])

        # Ajustar aspecto para visualización 3D
        ax.set_box_aspect([1, 0.6, 1])

        # Estilo de los planos
        for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
            axis.pane.set_edgecolor("black")
            axis.pane.set_alpha(0.8)
            axis.grid(True, linestyle="--", alpha=0.6, color="white")

        # Vista optimizada
        ax.view_init(elev=10, azim=-85)

        plt.tight_layout()
        show_plot(fig, "Estado de Residencia - Top 10")
        # ----------------------------------------------------------------------------------------------------------------------------------------------------

        # Medios de difusión
        st.subheader("Medios de Difusión de la Convocatoria")

        # Clasificación de medios (se mantiene igual)
        def classify_encuesta(value):
            value = str(value).lower()
            if re.search(r"facebook|Facebook|FB|fb", value):
                return "Facebook"
            elif re.search(r"noticia|news|noticias|periodico|diario|periodicos", value):
                return "Noticias"
            elif re.search(r"amigo|friend|compañero|contactos|contacto|amigos", value):
                return "Contactos"
            elif re.search(r"comercial|ad|anuncio|ad|TV|ad|tele|ad|television", value):
                return "Televisión"
            elif re.search(
                r"Redes sociales|ad|social media|social|redes sociales", value
            ):
                return "Redes sociales"
            elif re.search(r"internet|Internet|web|Web", value):
                return "Internet"
            elif re.search(r"WHATSAPP|what|whatsapp|whatsap|wa|WA|WhatsApp", value):
                return "WhatsApp"
            elif re.search(r"SSPC", value):
                return "Página oficial de la SSPC"
            else:
                return "Otro"

        # Procesar datos
        encuesta_classified = encuesta.apply(classify_encuesta)
        encuesta_counts = encuesta_classified.value_counts()

        # Crear figura 3D
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection="3d")

        # Configurar posiciones y dimensiones de las barras
        xpos = range(len(encuesta_counts))
        ypos = [0] * len(encuesta_counts)
        zpos = [0] * len(encuesta_counts)
        dx = [0.8] * len(encuesta_counts)  # Ancho constante
        dy = [0.8] * len(encuesta_counts)  # Profundidad (bases cuadradas)
        dz = encuesta_counts.values  # Altura variable

        # Crear barras 3D con color vino (#611232) como en el original
        bars = ax.bar3d(
            xpos, ypos, zpos, dx, dy, dz, color="#611232", shade=True, alpha=0.8
        )

        # Añadir etiquetas de valores absolutos ENCIMA de cada barra
        for i, (x, y, z) in enumerate(zip(xpos, ypos, dz)):
            ax.text(
                x + dx[i] / 2,
                y + dy[i] / 2,
                z + max(dz) * 0.05,
                f"{int(z)}",
                ha="center",
                va="bottom",
                color="black",
                fontsize=10,
                fontweight="bold",
                fontfamily="Noto Sans",
                bbox=dict(facecolor="white", alpha=0.5, edgecolor="none"),
            )

        # Configuración del gráfico
        ax.set_title("Distribución de Medios de Difusión", fontweight="bold", fontsize=14, fontfamily="Noto Sans")
        ax.set_zlabel("Cantidad", labelpad=30, fontfamily="Noto Sans", fontsize=12)
        ax.set_ylabel("")
        ax.set_xlabel("")
        ax.set_xticks([i + 0.4 for i in xpos])
        ax.set_xticklabels(encuesta_counts.index, rotation=0, ha="center", fontsize=5, fontweight="bold", family="Noto Sans")
        ax.set_yticks([])

        # Ajustar aspecto para visualización 3D
        ax.set_box_aspect([1, 0.6, 1])

        # Estilo de los planos
        for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
            axis.pane.set_edgecolor("black")
            axis.pane.set_alpha(0.8)
            axis.grid(True, linestyle="--", alpha=0.6, color="white")

        # Vista optimizada
        ax.view_init(elev=10, azim=-85)

        plt.tight_layout()
        show_plot(fig, "Medios de Difusión")
        # ----------------------------------------------------------------------------------------------------------------------------------------------------

        # Otras variables categóricas
        st.subheader("Otras Variables de Interés")

        variables = {
            "Pertenecen a alguna comunidad indígena o afrodescendiente": comunidad,
            "Se consideran parte de la comunidad LGBTIQ+": comunidadLGBT,
            # "Han ejercido algún cargo policial militar o afín": seguridadAntecedentes,
        }

        for title, var_data in variables.items():
            counts = var_data.value_counts()

            # Crear figura 3D
            fig = plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111, projection="3d")

            # Configurar posiciones y dimensiones de las barras
            xpos = range(len(counts))
            ypos = [0] * len(counts)
            zpos = [0] * len(counts)
            dx = [0.8] * len(counts)  # Ancho constante
            dy = [0.8] * len(counts)  # Profundidad (bases cuadradas)
            dz = counts.values  # Altura variable

            # Crear barras 3D con color rojo vino (#9b2247) como en el original
            bars = ax.bar3d(
                xpos,
                ypos,
                zpos,
                dx,
                dy,
                dz,
                color="#9b2247",
                shade=True,
                alpha=0.8,
                edgecolor="none",
            )

            # Añadir etiquetas de valores absolutos ENCIMA de cada barra
            for i, (x, y, z) in enumerate(zip(xpos, ypos, dz)):
                ax.text(
                    x + dx[i] / 2,
                    y + dy[i] / 2,
                    z + max(dz) * 0.05,
                    f"{int(z)}",
                    ha="center",
                    va="bottom",
                    color="black",
                    fontsize=10,
                    fontweight="bold",
                    fontfamily="Noto Sans",
                    bbox=dict(facecolor="white", alpha=0.5, edgecolor="none"),
                )

            # Configuración del gráfico
            ax.set_title(title, fontweight="bold", fontsize=14, fontfamily="Noto Sans")
            ax.set_zlabel("Cantidad", labelpad=30, fontfamily="Noto Sans", fontsize=12)
            ax.set_ylabel("")
            ax.set_xticks([i + 0.4 for i in xpos])
            ax.set_xticklabels(counts.index, rotation=0, ha="center", fontsize=12, fontweight="bold", family="Noto Sans")
            ax.set_yticks([])

            # Ajustar aspecto para visualización 3D
            ax.set_box_aspect([1, 0.6, 1])

            # Estilo de los planos
            for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
                axis.pane.set_edgecolor("black")
                axis.pane.set_alpha(0.8)
                axis.grid(True, linestyle="--", alpha=0.7, color="white")

            # Vista optimizada
            ax.view_init(elev=10, azim=-85)

            plt.tight_layout()
            show_plot(fig, f"{title}")

        # -------------------------------------------------------------------------------------------------------------
        # Obtener conteos
        seguridadAntecedentes_counts = seguridadAntecedentes.value_counts()

        # Crear figura 3D
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection="3d")

        # Configurar colores (manteniendo la paleta original)
        color = ["#1e5b4f"]

        # Posiciones para las barras
        xpos = range(len(seguridadAntecedentes_counts))
        ypos = [0] * len(seguridadAntecedentes_counts)
        zpos = [0] * len(seguridadAntecedentes_counts)

        # Dimensiones de las barras (bases cuadradas)
        dx = [0.8] * len(seguridadAntecedentes_counts)  # Ancho constante
        dy = [0.5] * len(seguridadAntecedentes_counts)  # Profundidad igual al ancho
        dz = seguridadAntecedentes_counts.values  # Altura variable

        # Crear gráfico de barras 3D
        bars = ax.bar3d(
            xpos, ypos, zpos, dx, dy, dz, color=color, shade=True, alpha=0.8
        )

        # Agregar valores absolutos encima de cada barra
        for i, (x, y, z) in enumerate(zip(xpos, ypos, dz)):
                    ax.text(
                        x + dx[i] / 2,
                        y + dy[i] / 2,
                        z + max(dz) * 0.05,
                        f"{int(z)}",
                        ha="center",
                        va="bottom",
                        color="black",
                        fontsize=10,
                        fontweight="bold",
                        fontfamily="Noto Sans",
                        bbox=dict(facecolor="white", alpha=0.5, edgecolor="none"),
                    )
        # Configuraciones del gráfico
        ax.set_title(
            "Distribución de Antecedentes de Seguridad",fontweight="bold", fontsize=14, fontfamily="Noto Sans"
        )
        ax.set_zlabel("Cantidad", labelpad=30, fontfamily="Noto Sans", fontsize=12)
        ax.set_ylabel("")
        ax.set_xlabel("")
        ax.set_xticks([i + dx[i] / 2 for i in xpos])
        ax.set_xticklabels(
            seguridadAntecedentes_counts.index, rotation=45, ha="center", fontsize=3, fontweight="bold", family="Noto Sans", wrap=True
        )
        ax.set_yticks([])

        # Ajustar aspecto para visualización 3D
        ax.set_box_aspect([1, 0.6, 1])

        # Estilo de los planos
        for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
            axis.pane.set_edgecolor("black")
            axis.pane.set_alpha(0.8)
            axis.grid(True, linestyle="--", alpha=0.6, color="white")

        # Vista optimizada
        ax.view_init(elev=10, azim=-85)

        plt.tight_layout()
        show_plot(fig, "Antecedentes de Seguridad")
        # -------------------------------------------------------------------------------------------------------------

        st.subheader("Puesto de Aplicación")

        # Obtener conteos
        puestoAplicacion_counts = puestoAplicacion.value_counts()

        # Crear figura 3D
        fig = plt.figure(
            figsize=(20, 10)
        )  # Tamaño ligeramente mayor para mejor visualización
        ax = fig.add_subplot(111, projection="3d")

        # Configurar colores (manteniendo la paleta original)
        colors = ["#611232"]

        # Posiciones para las barras
        xpos = range(len(puestoAplicacion_counts))
        ypos = [0] * len(puestoAplicacion_counts)
        zpos = [0] * len(puestoAplicacion_counts)

        # Dimensiones de las barras (bases cuadradas)
        dx = [0.8] * len(puestoAplicacion_counts)  # Ancho constante
        dy = [0.8] * len(puestoAplicacion_counts)  # Profundidad igual al ancho
        dz = puestoAplicacion_counts.values  # Altura variable

        # Crear gráfico de barras 3D
        bars = ax.bar3d(
            xpos, ypos, zpos, dx, dy, dz, color=color, shade=True, alpha=0.8
        )

        # Agregar valores absolutos encima de cada barra
        for i, (x, y, z) in enumerate(zip(xpos, ypos, dz)):
            ax.text(
                x + dx[i] / 2,
                y + dy[i] / 2,
                z + max(dz) * 0.05,
                f"{int(z)}",
                ha="center",
                va="bottom",
                color="black",
                fontsize=10,
                fontweight="bold",
                fontfamily="Noto Sans",
                bbox=dict(facecolor="white", alpha=0.5, edgecolor="none"),
            )


        # Configuraciones del gráfico
        ax.set_title(
            "Distribución por Puesto de Aplicación",  fontweight="bold", fontsize=14, fontfamily="Noto Sans"
        )
        ax.set_zlabel("Cantidad", labelpad=30, fontfamily="Noto Sans", fontsize=12)
        ax.set_ylabel("")
        ax.set_xlabel("", labelpad=10, fontsize=8, wrap=True)
        ax.set_xticks([i + dx[i] / 2 for i in xpos])
        ax.set_xticklabels(
            [
            col if len(col) <= 12 else "\n".join(re.findall(r'.{1,12}(?:\s+|$)', col))
            for col in puestoAplicacion_counts.index
            ], rotation=0, ha="center", fontsize=7, fontweight="bold", family="Noto Sans"
        )
        ax.set_yticks([])

        # Ajustar aspecto para visualización 3D
        ax.set_box_aspect([1.5, 0.6, 1])  # Más ancho para acomodar etiquetas largas

        # Estilo de los planos
        for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
            axis.pane.set_edgecolor("black")
            axis.pane.set_alpha(0.8)
            axis.grid(True, linestyle="--", alpha=0.6, color="white")

        # Vista optimizada para etiquetas largas
        ax.view_init(elev=10, azim=-85)

        plt.tight_layout()
        show_plot(fig, "Puesto de Aplicación")
        # -------------------------------------------------------------------------------------------------------------

    progress_bar.progress(100)
    status_text.text("¡Análisis completado!")
    st.success("El análisis se ha completado correctamente.")

    # Mostrar resumen de datos
    st.sidebar.header("Resumen de Datos")
    st.sidebar.write(f"Total de registros: {len(data)}")

    with tab4:
        st.header("Análisis por Estado")

        # Lista de estados disponibles
        estados_disponibles = sorted(estadoResidencia.unique())

        # Widget de selección de estado
        estado_seleccionado = st.selectbox(
            "Selecciona un estado para analizar:",
            options=estados_disponibles,
            index=0,
            key="estado_analisis",
        )

        if estado_seleccionado:
            # Filtrar datos por el estado seleccionado
            data_estado = data[data["ESTADO_RESIDENCIA"] == estado_seleccionado]

            if not data_estado.empty:
                st.success(
                    f"Analizando datos para {estado_seleccionado} ({len(data_estado)} registros)"
                )

                # Mostrar estadísticas básicas
                st.subheader(f"Resumen estadístico para {estado_seleccionado}")

                # Crear tabla resumen (valores absolutos)
                resumen_data = {
                    "Métrica": [
                        "Total registros",
                        "Edad promedio",
                        "Mujeres",
                        "Hombres",
                        "Escolaridad más común",
                        "Talla de calzado más común",
                    ],
                    "Valor": [
                        len(data_estado),
                        f"{data_estado['edad'].mean():.1f} años",
                        (
                            f"{data_estado[data_estado['SEXO'] == 'MUJER'].shape[0]}"
                            if "MUJER" in data_estado["SEXO"].unique()
                            else "0"
                        ),
                        (
                            f"{data_estado[data_estado['SEXO'] == 'HOMBRE'].shape[0]}"
                            if "HOMBRE" in data_estado["SEXO"].unique()
                            else "0"
                        ),
                        (
                            data_estado["ESCOLARIDAD"].mode()[0]
                            if not data_estado["ESCOLARIDAD"].mode().empty
                            else "N/A"
                        ),
                        (
                            data_estado["CALZADO_TALLA"].mode()[0]
                            if not data_estado["CALZADO_TALLA"].mode().empty
                            else "N/A"
                        ),
                    ],
                }

                resumen_df = pd.DataFrame(resumen_data)
                st.table(resumen_df)

                # Dividir en pestañas para diferentes tipos de análisis
                tab_estado1, tab_estado2 = st.tabs(
                    ["Distribuciones Generales", "Análisis por Sexo"]
                )
                # ---------------------------------------------------------------------------------------------------------------------------------------------------------
                with tab_estado1:
                    st.header(f"Distribuciones Generales para {estado_seleccionado}")

                    # Calcular los parámetros del histograma
                    min_age = max(18, int(data_estado["edad"].min())) - 1
                    max_age = int(data_estado["edad"].max()) + 1
                    age_bins = range(min_age, max_age + 1)
                    hist_values, bin_edges = np.histogram(
                        data_estado["edad"], bins=age_bins
                    )

                    # Crear figura 3D
                    fig = plt.figure(figsize=(14, 10))
                    ax = fig.add_subplot(111, projection="3d")

                    # Configurar posiciones y dimensiones
                    xpos = np.arange(len(hist_values))
                    ypos = np.zeros_like(xpos)
                    zpos = np.zeros_like(xpos)

                    # Configurar dimensiones de las barras
                    dx = 0.5 * np.ones_like(zpos)
                    dy = 0.5 * np.ones_like(zpos)
                    dz = hist_values

                    # Crear las barras 3D
                    ax.bar3d(
                        xpos,
                        ypos,
                        zpos,
                        dx,
                        dy,
                        dz,
                        color="#1e5b4f",
                        alpha=0.8,
                        edgecolor="none",
                    )

                    # Añadir etiquetas
                    ax.set_xticks(np.arange(len(hist_values)))
                    ax.set_xticklabels(
                        [f"{int(bin_edges[i])}" for i in range(len(hist_values))],
                        rotation=0,
                        ha="center",
                        fontsize=6,
                        fontweight="bold",
                        fontfamily="Noto Sans"
                    )
                    ax.set_yticks([])  # No necesitamos etiquetas en el eje Y
                    ax.set_zlabel("Cantidad de personas", labelpad=30, fontfamily="Noto Sans", fontsize=12)

                    # Añadir título y ajustar vista
                    ax.set_title(
                        f"Distribución por Edad en {estado_seleccionado}", fontsize=14, fontfamily="Noto Sans"
                    )
                    ax.view_init(elev=0, azim=-89)  # Ángulo de visualización

                    # Añadir etiquetas con valores en las barras
                    for i in range(len(xpos)):
                        if dz[i] > 0:  # Solo mostrar etiquetas para valores positivos
                            ax.text(
                                xpos[i] + dx[i] / 2,
                                ypos[i] + dy[i] / 2,
                                dz[i],
                                f"{int(dz[i])}",
                                ha="center",
                                va="bottom",
                                fontsize=9,
                                color="black",
                                bbox=dict(facecolor="white", alpha=0.5),
                            )

                    # Añadir línea de fondo para mejor referencia
                    ax.plot(xpos, ypos, zpos, color="gray", alpha=0.3)

                    plt.tight_layout()
                    st.pyplot(fig)
                # ---------------------------------------------------------------------------------------------------------------------------------------------------------
                with tab_estado2:
                    st.header(f"Análisis por Sexo en {estado_seleccionado}")

                    # Verificar qué sexos están presentes en el estado
                    sexos_presentes = data_estado["SEXO"].unique()

                    # Sexo y puesto de aplicación (valores absolutos)
                    if len(sexos_presentes) > 1:
                        st.subheader("Relación entre Sexo y Puesto de Aplicación")
                        sexo_puesto_counts = (
                            data_estado.groupby(["SEXO", "P5_ENCUESTA"])
                            .size()
                            .unstack(fill_value=0)
                        )

                        fig, ax = plt.subplots(figsize=(10, 6))
                        bar_width = 0.4
                        x = np.arange(len(sexo_puesto_counts.columns))

                        for sexo, color, offset in zip(
                            ["MUJER", "HOMBRE"],
                            ["#9b2247", "#1e5b4f"],
                            [-bar_width / 2, bar_width / 2],
                        ):
                            if sexo in sexo_puesto_counts.index:
                                ax.bar(
                                    x + offset,
                                    sexo_puesto_counts.loc[sexo],
                                    width=bar_width,
                                    label=sexo,
                                    color=color,
                                    alpha=0.8,
                                    edgecolor="white",
                                )
                                for i, puesto in enumerate(sexo_puesto_counts.columns):
                                    ax.text(
                                        x[i] + offset,
                                        sexo_puesto_counts.loc[sexo, puesto] / 2,
                                        f"{sexo_puesto_counts.loc[sexo, puesto]}",
                                        ha="center",
                                        va="center",
                                        fontsize=8,
                                        fontweight="bold",
                                        fontfamily="Noto Sans",
                                        color="black",
                                        bbox=dict(facecolor="white", alpha=0.5, edgecolor="none"),
                                    )

                        ax.set_title(
                            f"Relación entre Sexo y Puesto de Aplicación en {estado_seleccionado}"
                        )
                        ax.set_ylabel("Cantidad de personas", labelpad=30, fontfamily="Noto Sans", fontsize=12)
                        ax.set_xlabel("")
                        ax.set_xticks(x)
                        ax.set_xticklabels([col if len(col) <= 12 else "\n".join(re.findall(r'.{1,12}(?:\s+|$)', col))
                        for col in sexo_puesto_counts.columns
                        ], rotation=0, ha="center", fontsize=5 , fontweight="bold", family="Noto Sans"
                        )
                        ax.legend(title="Sexo")
                        ax.grid(axis="y", linestyle="--", alpha=0.6)
                        show_plot(fig, f"Análisis por Sexo en {estado_seleccionado}")

                    else:
                        st.info(
                            f"El estado {estado_seleccionado} solo tiene registros de {sexos_presentes[0]}, no se puede mostrar comparación por sexo."
                        )

                    # Sexo y estado civil (valores absolutos)
                    if len(sexos_presentes) < 1:
                        st.subheader("Relación entre Sexo y Estado Civil")
                        sexo_estado_civil_counts = (
                            data_estado.groupby(["SEXO", "ESTADO_CIVIL"])
                            .size()
                            .unstack(fill_value=0)
                        )

                        # Crear figura 3D
                        fig = plt.figure(figsize=(12, 8))
                        ax = fig.add_subplot(111, projection="3d")

                        # Configurar colores
                        colors = ["#af50e5", "#259f48"]

                        # Posiciones y dimensiones de las barras
                        xpos = np.arange(len(sexo_estado_civil_counts.columns))
                        ypos = np.zeros_like(xpos)
                        zpos = np.zeros_like(xpos)
                        dx = [0.4] * len(xpos)  # Ancho constante
                        dy = [0.4] * len(xpos)  # Profundidad constante

                        # Dibujar barras para cada sexo
                        for sexo, color, offset in zip(
                            ["MUJER", "HOMBRE"], colors, [-0.2, 0.2]
                        ):
                            if sexo in sexo_estado_civil_counts.index:
                                dz = sexo_estado_civil_counts.loc[sexo].values
                                ax.bar3d(
                                    xpos + offset,
                                    ypos,
                                    zpos,
                                    dx,
                                    dy,
                                    dz,
                                    color=color,
                                    alpha=0.8,
                                    edgecolor="white",
                                )

                                # Añadir etiquetas de valores
                                for i, value in enumerate(dz):
                                    if value > 0:
                                        ax.text(
                                            xpos[i] + offset + dx[i] / 2,
                                            ypos[i] + dy[i] / 2,
                                            zpos[i] + value + 1,
                                            f"{int(value)}",
                                            ha="center",
                                            va="bottom",
                                            fontsize=8,
                                            fontweight="bold",
                                            fontfamily="Noto Sans",
                                            color="black",
                                            bbox=dict(
                                                facecolor="white",
                                                alpha=0.5,
                                                edgecolor="none",
                                            ),
                                        )

                        # Configuración del gráfico
                        ax.set_title(
                            f"Relación entre Sexo y Estado Civil en {estado_seleccionado}",
                            fontweight="bold",
                            fontsize=14,
                            fontfamily="Noto Sans",
                        )
                        ax.set_zlabel(
                            "Cantidad de personas",
                            labelpad=30,
                            fontfamily="Noto Sans",
                            fontsize=12,
                        )
                        ax.set_ylabel("")
                        ax.set_xlabel("")
                        ax.set_xticks(xpos)
                        ax.set_xticklabels(
                            sexo_estado_civil_counts.columns,
                            rotation=0,
                            ha="center",
                            fontsize=10,
                            fontweight="bold",
                            fontfamily="Noto Sans",
                        )
                        ax.set_yticks([])

                        # Ajustar aspecto para visualización 3D
                        ax.set_box_aspect([1, 0.6, 1])

                        # Estilo de los planos
                        for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
                            axis.pane.set_edgecolor("black")
                            axis.pane.set_alpha(0.8)
                            axis.grid(True, linestyle="--", alpha=0.6, color="white")

                        # Vista optimizada
                        ax.view_init(elev=10, azim=-85)

                        plt.tight_layout()
                        show_plot(fig, f"Relación entre Sexo y Estado Civil en {estado_seleccionado}")

                    else:
                        st.subheader("Distribución de Estado Civil")
                        estado_civil_counts = data_estado["ESTADO_CIVIL"].value_counts()

                        # Crear figura 3D
                        fig = plt.figure(figsize=(12, 8))
                        ax = fig.add_subplot(111, projection="3d")

                        # Configurar colores
                        colors = ["#1e5b4f", "#9b2247", "#e6d194"]

                        # Posiciones y dimensiones de las barras
                        xpos = range(len(estado_civil_counts))
                        ypos = [0] * len(estado_civil_counts)
                        zpos = [0] * len(estado_civil_counts)
                        dx = [0.8] * len(estado_civil_counts)  # Ancho constante
                        dy = [0.8] * len(estado_civil_counts)  # Profundidad constante
                        dz = estado_civil_counts.values  # Altura variable

                        # Crear barras 3D
                        bars = ax.bar3d(
                            xpos, ypos, zpos, dx, dy, dz, color=colors, shade=True, alpha=0.8
                        )

                        # Añadir etiquetas de valores absolutos encima de cada barra
                        for i, (x, y, z) in enumerate(zip(xpos, ypos, dz)):
                            ax.text(
                                x + dx[i] / 2,
                                y + dy[i] / 2,
                                z + max(dz) * 0.05,
                                f"{int(z)}",
                                ha="center",
                                va="bottom",
                                color="black",
                                fontsize=10,
                                fontweight="bold",
                                fontfamily="Noto Sans",
                                bbox=dict(facecolor="white", alpha=0.5, edgecolor="none"),
                            )

                        # Configuración del gráfico
                        ax.set_title(
                            f"Distribución de Estado Civil en {estado_seleccionado}",
                            fontweight="bold",
                            fontsize=14,
                            fontfamily="Noto Sans",
                        )
                        ax.set_zlabel("Cantidad", labelpad=30, fontfamily="Noto Sans", fontsize=12)
                        ax.set_ylabel("")
                        ax.set_xlabel("")
                        ax.set_xticks([i + dx[i] / 2 for i in xpos])
                        ax.set_xticklabels(
                            estado_civil_counts.index,
                            rotation=0,
                            ha="center",
                            fontsize=10,
                            fontweight="bold",
                            fontfamily="Noto Sans",
                        )
                        ax.set_yticks([])

                        # Ajustar aspecto para visualización 3D
                        ax.set_box_aspect([1, 0.6, 1])

                        # Estilo de los planos
                        for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
                            axis.pane.set_edgecolor("black")
                            axis.pane.set_alpha(0.8)
                            axis.grid(True, linestyle="--", alpha=0.6, color="white")

                        # Vista optimizada
                        ax.view_init(elev=10, azim=-85)

                        plt.tight_layout()
                        show_plot(fig, f"Distribución de Estado Civil en {estado_seleccionado}")

                    # Comunidad indígena y LGBT (valores absolutos)
                    st.subheader("Pertenencia a Comunidad Indígena o LGBT")
                    for var, title, color in zip(
                        ["P2_ENCUESTA", "P3_ENCUESTA"],
                        ["Comunidad Indígena", "Comunidad LGBT"],
                        ["#611232", "#161a1d"],
                    ):
                        counts = data_estado[var].value_counts()

                        # Crear figura 3D
                        fig = plt.figure(figsize=(12, 8))
                        ax = fig.add_subplot(111, projection="3d")

                        # Configurar posiciones y dimensiones de las barras
                        xpos = range(len(counts))
                        ypos = [0] * len(counts)
                        zpos = [0] * len(counts)
                        dx = [0.8] * len(counts)  # Ancho constante
                        dy = [0.8] * len(counts)  # Profundidad (bases cuadradas)
                        dz = counts.values  # Altura variable

                        # Crear barras 3D
                        bars = ax.bar3d(
                            xpos, ypos, zpos, dx, dy, dz, color=color, shade=True, alpha=0.8
                        )

                        # Añadir etiquetas de valores absolutos encima de cada barra
                        for i, (x, y, z) in enumerate(zip(xpos, ypos, dz)):
                            ax.text(
                                x + dx[i] / 2,
                                y + dy[i] / 2,
                                z + max(dz) * 0.05,
                                f"{int(z)}",
                                ha="center",
                                va="bottom",
                                color="black",
                                fontsize=10,
                                fontweight="bold",
                                fontfamily="Noto Sans",
                                bbox=dict(facecolor="white", alpha=0.5, edgecolor="none"),
                            )

                        # Configuración del gráfico
                        ax.set_title(
                            f"Distribución de {title} en {estado_seleccionado}",
                            fontweight="bold",
                            fontsize=14,
                            fontfamily="Noto Sans",
                        )
                        ax.set_zlabel("Cantidad", labelpad=30, fontfamily="Noto Sans", fontsize=12)
                        ax.set_ylabel("")
                        ax.set_xlabel("")
                        ax.set_xticks([i + dx[i] / 2 for i in xpos])
                        ax.set_xticklabels(
                            counts.index,
                            rotation=0,
                            ha="center",
                            fontsize=10,
                            fontweight="bold",
                            fontfamily="Noto Sans",
                        )
                        ax.set_yticks([])

                        # Ajustar aspecto para visualización 3D
                        ax.set_box_aspect([1, 0.6, 1])

                        # Estilo de los planos
                        for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
                            axis.pane.set_edgecolor("black")
                            axis.pane.set_alpha(0.8)
                            axis.grid(True, linestyle="--", alpha=0.6, color="white")

                        # Vista optimizada
                        ax.view_init(elev=10, azim=-85)

                        plt.tight_layout()
                        show_plot(fig, f"{title} en {estado_seleccionado}")

                    # Antecedentes de seguridad (valores absolutos)
                    st.subheader("Antecedentes de Seguridad")
                    seguridad_counts = data_estado["P4_ENCUESTA"].value_counts()

                    # Crear figura 3D
                    fig = plt.figure(figsize=(12, 8))
                    ax = fig.add_subplot(111, projection="3d")

                    # Configurar colores
                    colors = ["#1e5b4f", "#9b2247", "#e6d194", "#611232", "#161a1d"]

                    # Posiciones y dimensiones de las barras
                    xpos = range(len(seguridad_counts))
                    ypos = [0] * len(seguridad_counts)
                    zpos = [0] * len(seguridad_counts)
                    dx = [0.8] * len(seguridad_counts)  # Ancho constante
                    dy = [0.8] * len(seguridad_counts)  # Profundidad constante
                    dz = seguridad_counts.values  # Altura variable

                    # Crear barras 3D
                    bars = ax.bar3d(
                        xpos, ypos, zpos, dx, dy, dz, color=colors, shade=True, alpha=0.8
                    )

                    # Añadir etiquetas de valores absolutos encima de cada barra
                    for i, (x, y, z) in enumerate(zip(xpos, ypos, dz)):
                        ax.text(
                            x + dx[i] / 2,
                            y + dy[i] / 2,
                            z + max(dz) * 0.05,
                            f"{int(z)}",
                            ha="center",
                            va="bottom",
                            color="black",
                            fontsize=10,
                            fontweight="bold",
                            fontfamily="Noto Sans",
                            bbox=dict(facecolor="white", alpha=0.5, edgecolor="none"),
                        )

                    # Configuración del gráfico
                    ax.set_title(
                        f"Distribución de Antecedentes de Seguridad en {estado_seleccionado}",
                        fontweight="bold",
                        fontsize=14,
                        fontfamily="Noto Sans",
                    )
                    ax.set_zlabel("Cantidad", labelpad=30, fontfamily="Noto Sans", fontsize=12)
                    ax.set_ylabel("")
                    ax.set_xlabel("")
                    ax.set_xticks([i + dx[i] / 2 for i in xpos])
                    ax.set_xticklabels(
                        [
                        col if len(col) <= 12 else "\n".join(re.findall(r'.{1,12}(?:\s+|$)', col))
                        for col in seguridad_counts.index
                        ],
                        rotation=0,
                        ha="center",
                        fontsize=7,
                        fontweight="bold",
                        fontfamily="Noto Sans",
                    )
                    ax.set_yticks([])

                    # Ajustar aspecto para visualización 3D
                    ax.set_box_aspect([1, 0.6, 1])

                    # Estilo de los planos
                    for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
                        axis.pane.set_edgecolor("black")
                        axis.pane.set_alpha(0.8)
                        axis.grid(True, linestyle="--", alpha=0.6, color="white")

                    # Vista optimizada
                    ax.view_init(elev=10, azim=-85)

                    plt.tight_layout()
                    show_plot(fig, f"Distribución de Antecedentes de Seguridad en {estado_seleccionado}")

            else:
                st.warning(
                    f"No se encontraron registros para el estado: {estado_seleccionado}"
                )

else:
    st.info("Por favor, sube un archivo para comenzar el análisis.")

# Créditos
st.sidebar.markdown("---")
st.sidebar.markdown("**Desarrollado por:**  \nEquipo de Análisis de Datos")

# Haciendo un botón en la barra lateral de Streamlit para descargar el archivo creado
with st.sidebar:
    try:
        with open("reclutamiento_data_filtrado.xlsx", "rb") as file:
            st.download_button(
                label="Descargar archivo filtrado",
                data=file.read(),
                file_name="reclutamiento_data_filtrado.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_button",
            )
    except FileNotFoundError:
        st.error(
            "El archivo 'reclutamiento_data_filtrado.xlsx' no se encontró. Asegúrate de que se haya generado correctamente."
        )
