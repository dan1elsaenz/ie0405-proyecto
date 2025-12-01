"""
Módulo para analizar tiempos entre eventos de un flujo de eventos MQTT.

Este script:
- Carga timestamps desde una base de datos.
- Calcula los tiempos entre eventos (time_between_data).
- Calcula estadística descriptiva de los datos.
- Utiliza Fitter para comparar varias distribuciones de probabilidad.
- Calcula los momentos teóricos del modelo seleccionado (media, varianza,
  desviación estándar, skewness y kurtosis).
- Genera gráficos descriptivos (histograma de datos y ajuste de mejor
  distribución).
"""

import os
import logging

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from fitter import Fitter, get_common_distributions


logger = logging.getLogger(__name__)


def load_time_between_data(
    database_url: str,
    table_name: str = "event",
    timestamp_column: str = "timestamp",
) -> np.ndarray:
    """
    Carga timestamps desde la base de datos y calcula los tiempos entre
    eventos.

    Parameters
    ----------
    database_url : str
        URL de conexión a la base de datos.
    table_name : str
        Nombre de la tabla que contiene los eventos. Por defecto, "event".
    timestamp_column : str
        Nombre de la columna que contiene los timestamps. Por defecto,
        "timestamp".

    Returns
    -------
    np.ndarray
        Arreglo unidimensional de tiempos entre eventos en segundos
        (time_between_data), calculado como la diferencia entre timestamps
        consecutivos.

    Raises
    ------
    RuntimeError
        Si ocurre un problema al acceder a la base de datos, la tabla está
        vacía, la columna de timestamp no existe o no hay suficientes
        registros para calcular al menos un intervalo de tiempo.
    """
    try:
        engine = create_engine(database_url)

        # Leer la columna de timestamps y ordenarla en forma ascendente para
        # garantizar que las diferencias se calculen en el orden temporal
        query = (
            f"SELECT {timestamp_column} "
            f"FROM {table_name} ORDER BY {timestamp_column} ASC"
        )
        df = pd.read_sql(query, con=engine)
    except SQLAlchemyError as exc:
        logger.error("Error al acceder a la base de datos: %s", exc)
        raise RuntimeError(
            "No se pudieron cargar los datos desde la base de datos."
        ) from exc

    # Manejo de errores
    if df.empty:
        logger.error("La tabla '%s' no contiene filas; sin datos.", table_name)
        raise RuntimeError(
            "La tabla de eventos está vacía; no hay datos para analizar."
        )

    try:
        # Asegurar que la columna sea de tipo datetime para poder usar diff()
        df[timestamp_column] = pd.to_datetime(df[timestamp_column])

        # Calcular la diferencia entre timestamps consecutivos
        df["time_between_data"] = df[timestamp_column].diff().dt.total_seconds()
    except KeyError as exc:
        logger.error(
            "La columna '%s' no existe en la tabla '%s'.",
            timestamp_column,
            table_name,
        )
        raise RuntimeError(
            "La estructura de la tabla no contiene la columna de timestamp."
        ) from exc

    # El primer valor es NaN, por lo que se elimina antes de convertir a numpy
    time_between_data = df["time_between_data"].dropna().to_numpy()

    if time_between_data.size == 0:
        logger.error("No se pudieron calcular tiempos entre eventos.")
        raise RuntimeError(
            "No hay suficientes registros para calcular tiempos entre eventos."
        )

    return time_between_data


def compute_descriptive_stats(time_between_data: np.ndarray) -> pd.Series:
    """
    Calcula estadísticas experimentales de los tiempos entre eventos.

    Parameters
    ----------
    time_between_data : np.ndarray
        Arreglo unidimensional con los tiempos entre eventos en segundos.

    Returns
    -------
    pd.Series
        Serie con métricas descriptivas básicas:
        - n: número de muestras
        - min, max: valores mínimo y máximo
        - mean, median: media y mediana
        - std: desviación estándar muestral
        - q25, q75: cuantiles 25% y 75%
        - skewness: inclinación
        - kurtosis
    """
    s = pd.Series(time_between_data)
    stats_desc = pd.Series(
        {
            "n": s.size,
            "min": s.min(),
            "max": s.max(),
            "mean": s.mean(),
            "median": s.median(),
            "std": s.std(),
            "q25": s.quantile(0.25),
            "q75": s.quantile(0.75),
            "skewness": s.skew(),
            "kurtosis": s.kurtosis(),
        }
    )
    return stats_desc


def fit_candidate_distributions(
    time_between_data: np.ndarray,
    distributions: list[str] | None = None,
    use_common_distributions: bool = True,
) -> dict:
    """
    Ajusta distribuciones de probabilidad usando Fitter y devuelve la mejor.

    Parameters
    ----------
    time_between_data : np.ndarray
        Arreglo de tiempos entre eventos en segundos que se utiliza para
        realizar el ajuste.
    distributions : list[str] or None
        Lista de nombres de distribuciones de scipy.stats a probar. Si es None,
        el conjunto de distribuciones a usar depende de
        use_common_distributions.
    use_common_distributions : bool
        Si es True y distributions es None, se utiliza
        get_common_distributions(). Si es False y distributions es
        None, Fitter utiliza su conjunto de distribuciones por defecto.

    Returns
    -------
    dict
        Diccionario con la mejor distribución según Fitter.
    """
    # Determinar qué conjunto de distribuciones usar
    if distributions is not None:
        dist_list = distributions
    elif use_common_distributions:
        dist_list = get_common_distributions()
    else:
        # Fitter usa todas las distribuciones por defecto
        dist_list = None

    if dist_list is None:
        f = Fitter(time_between_data)
    else:
        f = Fitter(time_between_data, distributions=dist_list)

    # Salto de línea para separar el log de Fitter de la salida previa
    print()
    logger.info("Ajustando distribuciones candidatas con Fitter...")
    f.fit()

    best = f.get_best(method="sumsquare_error")
    best_dist_name = list(best.keys())[0]
    best_params = list(best.values())[0]

    return {"dist": best_dist_name, "params": best_params}


def compute_model_moments(best_model: dict) -> pd.Series:
    """
    Calcula los momentos teóricos del modelo de probabilidad seleccionado.

    Se utilizan las funciones de scipy.stats para obtener:

    - media
    - varianza
    - desviación estándar
    - skewness
    - kurtosis

    Parameters
    ----------
    best_model : dict
        Diccionario con la información del modelo seleccionado.

    Returns
    -------
    pd.Series
        Serie con los momentos teóricos del modelo con las siguientes llaves:
        - mean_model
        - var_model
        - std_model
        - skewness_model
        - kurtosis_model
    """
    dist_name = best_model["dist"]
    params = best_model["params"]

    # Obtener el objeto de distribución de scipy.stats
    dist = getattr(stats, dist_name)

    # mean, var, skew, kurtosis
    mean, var, skew, kurt = dist.stats(**params, moments="mvsk")
    std = np.sqrt(var)

    moments = pd.Series(
        {
            "mean_model": float(mean),
            "var_model": float(var),
            "std_model": float(std),
            "skewness_model": float(skew),
            "kurtosis_model": float(kurt),
        }
    )
    return moments


def _freedman_diaconis_bins(data: np.ndarray) -> int:
    """
    Calcula el número de bins según la regla de Freedman–Diaconis.

    La regla usa el rango intercuartílico para definir el ancho del bin y, a
    partir de este, el número de bins.
    Es un algoritmo común utilizado para estandarizar este procedimiento.

    Parameters
    ----------
    data : np.ndarray
        Arreglo de datos numéricos sobre el cual se desea calcular el número
        recomendado de bins.

    Returns
    -------
    int
        Número de bins a utilizar en un histograma.
    """
    s = pd.Series(data)
    iqr = s.quantile(0.75) - s.quantile(0.25)
    if iqr == 0:
        return 10
    bin_width = 2 * iqr / (len(s) ** (1 / 3))
    if bin_width <= 0:
        return 10
    bins = int(np.ceil((s.max() - s.min()) / bin_width))
    return max(bins, 10)


def plot_histograma_datos(
    time_between_data: np.ndarray,
    output_path: str,
) -> None:
    """
    Genera una gráfica con el histograma de los tiempos entre eventos.

    El histograma se construye usando seaborn.histplot y se formatea con un
    estilo definido, además de aplicar configuración de matplotlib para fondos
    blancos y grid.

    Parameters
    ----------
    time_between_data : np.ndarray
        Arreglo de tiempos entre eventos en segundos.
    output_path : str
        Ruta de salida donde se guardará la figura en formato SVG. Si el
        directorio no existe, se crea automáticamente.
    """
    n_bins = _freedman_diaconis_bins(time_between_data)

    # Formato de estilo clásico para el histograma
    plt.style.use("classic")
    mpl.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "black",
            "axes.grid": True,
            "grid.color": "0.8",
            "grid.linestyle": ":",
            "grid.linewidth": 0.8,
            "axes.spines.top": True,
            "axes.spines.right": True,
            "axes.linewidth": 1.0,
            "xtick.direction": "in",
            "ytick.direction": "in",
            "font.size": 11,
        }
    )
    sns.set_theme(style="whitegrid")

    df = pd.DataFrame(time_between_data, columns=["time_between_data"])

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.histplot(
        df["time_between_data"],
        bins=n_bins,
        stat="density",
        color="C0",
        alpha=0.7,
        edgecolor="black",
        ax=ax,
    )
    ax.set_title("Histograma de tiempos entre eventos")
    ax.set_xlabel("Tiempo entre eventos [s]")
    ax.set_ylabel("Densidad")

    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, format="svg", bbox_inches="tight")
    plt.close(fig)


def plot_histograma_mejor_ajuste(
    time_between_data: np.ndarray,
    best_model: dict,
    output_path: str,
) -> None:
    """
    Genera un histograma de los datos y la curva de la mejor distribución.

    Se combina el histograma de los tiempos entre eventos con la curva de
    densidad de la distribución seleccionada por Fitter, para visualizar
    qué tan bien se ajusta el modelo al conjunto de datos.

    Parameters
    ----------
    time_between_data : np.ndarray
        Arreglo de tiempos entre eventos en segundos.
    best_model : dict
        Diccionario con las llaves:
        - "dist": nombre de la distribución seleccionada.
        - "params": parámetros ajustados para dicha distribución.
    output_path : str
        Ruta de salida donde se guardará la figura en formato SVG. Si el
        directorio no existe, se crea automáticamente.
    """
    n_bins = _freedman_diaconis_bins(time_between_data)

    dist_name = best_model["dist"]
    params = best_model["params"]

    # Obtener el objeto de distribución de scipy.stats
    dist = getattr(stats, dist_name)

    # Rango para la curva
    x_max = np.quantile(time_between_data, 0.99)
    x_values = np.linspace(0, x_max, 300)
    pdf_values = dist.pdf(x_values, **params)

    # Estilo definido
    plt.style.use("classic")
    mpl.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "black",
            "axes.grid": True,
            "grid.color": "0.8",
            "grid.linestyle": ":",
            "grid.linewidth": 0.8,
            "axes.spines.top": True,
            "axes.spines.right": True,
            "axes.linewidth": 1.0,
            "xtick.direction": "in",
            "ytick.direction": "in",
            "font.size": 11,
        }
    )
    sns.set_theme(style="whitegrid")

    df = pd.DataFrame(time_between_data, columns=["time_between_data"])

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.histplot(
        df["time_between_data"],
        bins=n_bins,
        stat="density",
        color="C1",
        alpha=0.6,
        edgecolor="black",
        label="Datos empíricos",
        ax=ax,
    )

    ax.plot(
        x_values,
        pdf_values,
        "k-",
        linewidth=1.5,
        label=f"Mejor ajuste: {dist_name}",
    )

    ax.set_title("Histograma y curva de mejor ajuste")
    ax.set_xlabel("Tiempo entre eventos [s]")
    ax.set_ylabel("Densidad")
    ax.legend()

    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, format="svg", bbox_inches="tight")
    plt.close(fig)


def _print_descriptive_stats_table(stats_desc: pd.Series) -> None:
    """
    Imprime las estadísticas experimentales en formato tabla.

    Parameters
    ----------
    stats_desc : pd.Series
        Serie con las métricas calculadas por compute_descriptive_stats().
        Cada elemento se imprime como una fila de la tabla, con el índice como
        nombre de la métrica y su valor correspondiente.
    """
    df_stats = stats_desc.to_frame(name="Valor")
    print(df_stats.to_string(float_format=lambda x: f"{x:0.6f}"))


def _print_comparison_table(stats_desc: pd.Series, model_moments: pd.Series) -> None:
    """
    Imprime una tabla comparando momentos experimentales y del modelo.

    La tabla incluye media, varianza, desviación estándar, skewness y
    kurtosis para los datos experimentales y para el modelo ajustado.
    Se imprime también la tasa lambda estimada cuando el modelo es exponencial.

    Parameters
    ----------
    stats_desc : pd.Series
        Serie con estadísticas experimentales de los datos.
    model_moments : pd.Series
        Serie con los momentos teóricos del modelo.
    """
    var_datos = stats_desc["std"] ** 2

    data = {
        "Datos": {
            "Media": stats_desc["mean"],
            "Varianza": var_datos,
            "Desv. estándar": stats_desc["std"],
            "Skewness": stats_desc["skewness"],
            "Kurtosis": stats_desc["kurtosis"],
        },
        "Modelo exponencial": {
            "Media": model_moments["mean_model"],
            "Varianza": model_moments["var_model"],
            "Desv. estándar": model_moments["std_model"],
            "Skewness": model_moments["skewness_model"],
            "Kurtosis": model_moments["kurtosis_model"],
        },
    }
    df_comp = pd.DataFrame(data)

    print("\nComparación de momentos:\n")
    print(df_comp.to_string(float_format=lambda x: f"{x:0.6f}"))


def _check_sqlite_file(database_url: str) -> bool:
    """
    Verifica que el archivo SQLite exista cuando se usa sqlite:///.

    Esto permite detectar errores en la ruta de DATABASE_URL cuando se está
    trabajando con un archivo de base de datos local.

    Parameters
    ----------
    database_url : str
        URL de conexión a la base de datos. Si comienza con sqlite:///,
        se interpreta como una ruta a un archivo SQLite.

    Returns
    -------
    bool
        True si la URL no corresponde a un archivo SQLite o si el archivo
        existe. False si la URL apunta a un archivo SQLite que no se
        encuentra en el sistema de archivos.
    """
    prefix = "sqlite:///"
    if not database_url.startswith(prefix):
        return True

    path = database_url[len(prefix) :]
    if not path or path == ":memory:":
        return True

    if not os.path.exists(path):
        logger.error(
            "No se encontró el archivo de base de datos SQLite en '%s'. "
            "Verifique la variable DATABASE_URL.",
            path,
        )
        return False

    return True


def main() -> None:
    """
    Punto de entrada principal del script.

    Esta función:
    - Configura el sistema de logging.
    - Carga la variable de entorno DATABASE_URL desde el archivo .env.
    - Verifica la existencia del archivo SQLite.
    - Carga los tiempos entre eventos desde la base de datos.
    - Calcula estadística descriptiva y la imprime en consola.
    - Ajusta distribuciones de probabilidad usando Fitter.
    - Calcula los momentos teóricos del mejor modelo.
    - Genera y guarda las figuras de histograma y mejor ajuste.
    - Imprime un resumen del ajuste exponencial si la distribución ganadora
      es expon.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s | %(message)s",
    )

    load_dotenv()
    database_url = os.getenv("DATABASE_URL", "sqlite:///events.db")

    logger.info("Iniciando análisis de tiempos entre eventos...")
    logger.info("Usando base de datos: %s", database_url)

    # Verificación temprana cuando se usa SQLite en archivo
    if not _check_sqlite_file(database_url):
        logger.error("No se puede continuar sin una base de datos válida.")
        return

    # Cargar tiempos entre eventos desde la BD
    try:
        time_between_data = load_time_between_data(database_url)
    except RuntimeError as exc:
        logger.error("%s", exc)
        logger.error("El programa finalizará sin realizar el análisis.")
        return

    logger.info("Se cargaron %d tiempos.", len(time_between_data))

    # Datos experimentales
    print("\nEstadísticas experimentales de time_between_data (s):\n")
    stats_desc = compute_descriptive_stats(time_between_data)
    _print_descriptive_stats_table(stats_desc)

    # Ajustar varias distribuciones con Fitter
    best_model = fit_candidate_distributions(
        time_between_data,
        use_common_distributions=True,
    )

    # Calcular momentos teóricos del modelo seleccionado
    model_moments = compute_model_moments(best_model)

    # Graficar histograma solo de datos
    output_hist_datos = "docs/images/histograma_tiempos_entre_datos.svg"
    plot_histograma_datos(
        time_between_data=time_between_data,
        output_path=output_hist_datos,
    )

    # Graficar histograma y curva de mejor ajuste
    output_hist_ajuste = "docs/images/histograma_mejor_ajuste.svg"
    plot_histograma_mejor_ajuste(
        time_between_data=time_between_data,
        best_model=best_model,
        output_path=output_hist_ajuste,
    )
    logger.info("Gráficas guardadas en docs/images/.")

    # Resumen del modelo exponencial
    dist_name = best_model["dist"]
    params = best_model["params"]

    if dist_name == "expon":
        loc = params.get("loc", 0.0)
        scale = params.get("scale", 1.0)
        lambda_estimate = 1.0 / scale

        print("\nResultados del ajuste exponencial\n")
        print(f"loc (esperado ~0): {loc:.6f}")
        print(f"scale (1/λ):       {scale:.6f} s")
        print(f"λ estimado:        {lambda_estimate:.6f} 1/s")

        _print_comparison_table(
            stats_desc, model_moments
        )
    else:
        print("\nModelo seleccionado no exponencial:\n")
        print(f"Distribución: {dist_name}")
        print(f"Parámetros: {params}\n")

    logger.info("Análisis completado correctamente.")


if __name__ == "__main__":
    main()
