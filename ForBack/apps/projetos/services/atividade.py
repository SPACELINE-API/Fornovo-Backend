from django.utils import timezone

from apps.projetos.models import Projeto, Arquivo

MESES_ABREV = [
    'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
    'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez',
]

TIPOS_MEMORIAL = ('xlsx', 'docx')


def _ultimos_periodos_mensais(quantidade=6):
    hoje = timezone.localdate()
    periodos = []

    for offset in range(quantidade - 1, -1, -1):
        mes = hoje.month - offset
        ano = hoje.year
        while mes <= 0:
            mes += 12
            ano -= 1
        periodos.append((ano, mes))

    return periodos


def atividade_ultimos_meses(meses=6):
    periodos = _ultimos_periodos_mensais(meses)
    projetos_data = []
    memoriais_data = []

    for ano, mes in periodos:
        label = MESES_ABREV[mes - 1]
        projetos_data.append({
            'mes': label,
            'quantidade': Projeto.objects.filter(
                criado_em__year=ano,
                criado_em__month=mes,
            ).count(),
        })
        memoriais_data.append({
            'mes': label,
            'quantidade': Arquivo.objects.filter(
                tipo_arquivo__in=TIPOS_MEMORIAL,
                criado_em__year=ano,
                criado_em__month=mes,
            ).count(),
        })

    return {
        'projetos': projetos_data,
        'memoriais': memoriais_data,
    }
