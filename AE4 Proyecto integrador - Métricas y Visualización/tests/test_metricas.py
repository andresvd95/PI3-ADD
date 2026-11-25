"""Pruebas de las métricas que usan la aplicación de Streamlit y el documento final."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import metricas as m  # noqa: E402


@pytest.fixture(scope="module")
def resultado():
    return m.calcular_todo(m.localizar_raiz(Path(__file__)))


def test_tablas_coinciden_con_resultados_de_ae3(resultado):
    assert resultado["verificacion"]["coincide_con_ae3"].all()


def test_cada_tabla_conserva_pasajeros_y_sobrevivientes(resultado):
    for tabla in resultado["tablas"].values():
        assert int(tabla["pasajeros"].sum()) == 891
        assert int(tabla["sobrevivientes"].sum()) == 342
        assert tabla["tasa_supervivencia_pct"].between(0, 100).all()


def test_orden_logico_de_grupos(resultado):
    edad = resultado["tablas"]["pregunta_4_supervivencia_por_grupo_edad"]["grupo_edad"].tolist()
    assert edad == m.ORDEN["grupo_edad"]
    assert resultado["tablas"]["pregunta_2_supervivencia_por_clase"]["clase"].tolist() == m.ORDEN["clase"]


def test_clase_sexo_suma_el_total(resultado):
    cs = resultado["clase_sexo"]
    assert len(cs) == 6
    assert int(cs["pasajeros"].sum()) == 891
    assert int(cs["sobrevivientes"].sum()) == 342


def test_tarifas_suman_el_total_registrado(resultado):
    tarifas = resultado["tarifas"]
    total = resultado["datos"]["tarifa"].sum()
    assert tarifas["tarifa_total"].sum() == pytest.approx(total, abs=0.05)
    assert tarifas["participacion_tarifa_pct"].sum() == pytest.approx(100, abs=0.05)
    assert int(tarifas["pasajes_tarifa_cero"].sum()) == 15
