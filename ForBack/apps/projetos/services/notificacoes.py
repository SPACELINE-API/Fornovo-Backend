from django.utils import timezone

from apps.projetos.models import Notificacao, Projeto

TIPO_POR_STATUS = {
    'Em revisão': 'alerta',
    'Concluído': 'sucesso',
    'Em andamento': 'info',
    'Pendente': 'info',
}

MENSAGEM_POR_STATUS = {
    'Em revisão': 'Projeto "{nome}" entrou em revisão',
    'Concluído': 'Projeto "{nome}" concluído com sucesso',
    'Em andamento': 'Projeto "{nome}" em andamento',
    'Pendente': 'Projeto "{nome}" marcado como pendente',
}


def usuario_da_requisicao(request):
    user = getattr(request, 'user', None)
    if user and getattr(user, 'is_authenticated', False):
        return getattr(user, 'nome_usuario', None) or 'Sistema'
    return 'Sistema'


def registrar(
    tipo,
    mensagem,
    usuario='Sistema',
    referencia_tipo=None,
    referencia_id=None,
):
    return Notificacao.objects.create(
        tipo=tipo,
        mensagem=mensagem,
        usuario=usuario,
        referencia_tipo=referencia_tipo,
        referencia_id=str(referencia_id) if referencia_id is not None else None,
    )


def registrar_se_unica(referencia_tipo, referencia_id, mensagem, **kwargs):
    if Notificacao.objects.filter(
        referencia_tipo=referencia_tipo,
        referencia_id=str(referencia_id),
        mensagem=mensagem,
    ).exists():
        return None
    return registrar(
        referencia_tipo=referencia_tipo,
        referencia_id=referencia_id,
        mensagem=mensagem,
        **kwargs,
    )


def registrar_novo_projeto(projeto, usuario):
    registrar(
        tipo='info',
        mensagem=f'Novo projeto criado: "{projeto.nome_projeto}"',
        usuario=usuario,
        referencia_tipo='projeto',
        referencia_id=projeto.id_projeto,
    )


def registrar_mudanca_status_projeto(projeto, status_novo, usuario):
    template = MENSAGEM_POR_STATUS.get(status_novo)
    if not template:
        return None

    return registrar(
        tipo=TIPO_POR_STATUS.get(status_novo, 'info'),
        mensagem=template.format(nome=projeto.nome_projeto),
        usuario=usuario,
        referencia_tipo='projeto',
        referencia_id=projeto.id_projeto,
    )


def registrar_arquivo_projeto(projeto, nome_arquivo, tipo_arquivo, usuario):
    if tipo_arquivo in ('xlsx', 'docx'):
        registrar(
            tipo='sucesso',
            mensagem=f'Memorial "{nome_arquivo}" gerado para "{projeto.nome_projeto}"',
            usuario=usuario,
            referencia_tipo='memorial',
            referencia_id=projeto.id_projeto,
        )
    else:
        registrar(
            tipo='info',
            mensagem=f'Arquivo "{nome_arquivo}" enviado ao projeto "{projeto.nome_projeto}"',
            usuario=usuario,
            referencia_tipo='arquivo',
            referencia_id=projeto.id_projeto,
        )


def registrar_norma_criada(norma, usuario='Sistema'):
    registrar(
        tipo='info',
        mensagem=f'Norma {norma.codigo} cadastrada no sistema',
        usuario=usuario,
        referencia_tipo='norma',
        referencia_id=norma.id_norma,
    )


def registrar_norma_atualizada(norma, usuario='Sistema'):
    registrar(
        tipo='info',
        mensagem=f'Norma {norma.codigo} foi atualizada',
        usuario=usuario,
        referencia_tipo='norma',
        referencia_id=norma.id_norma,
    )


def registrar_norma_status(norma, usuario='Sistema'):
    registrar(
        tipo='info',
        mensagem=f'Norma {norma.codigo} está {norma.status}',
        usuario=usuario,
        referencia_tipo='norma',
        referencia_id=norma.id_norma,
    )


def registrar_novo_funcionario(usuario_criado, admin_nome):
    registrar(
        tipo='info',
        mensagem=f'Novo funcionário cadastrado: {usuario_criado.nome_usuario}',
        usuario=admin_nome,
        referencia_tipo='usuario',
        referencia_id=usuario_criado.id_usuario,
    )


def registrar_levantamento_campo(projeto, usuario='Sistema'):
    registrar(
        tipo='alerta',
        mensagem=f'Levantamento de campo registrado em "{projeto.nome_projeto}" — pendente de revisão',
        usuario=usuario,
        referencia_tipo='levantamento',
        referencia_id=projeto.id_projeto,
    )


def registrar_projetos_atrasados():
    hoje = timezone.localdate()
    for projeto in Projeto.objects.filter(
        data_inicio__isnull=False,
        data_fim__isnull=False,
        data_fim__lt=hoje,
    ).exclude(status='Concluído'):
        registrar_se_unica(
            referencia_tipo='projeto_atrasado',
            referencia_id=projeto.id_projeto,
            tipo='erro',
            mensagem=f'Projeto "{projeto.nome_projeto}" está atrasado',
            usuario='Sistema',
        )


def popular_historico_inicial():
    if Notificacao.objects.exists():
        return

    for projeto in Projeto.objects.select_related('engenheiro').order_by('-criado_em')[:8]:
        engenheiro = projeto.engenheiro.nome_usuario if projeto.engenheiro else 'Sistema'
        Notificacao.objects.create(
            tipo='info',
            mensagem=f'Projeto "{projeto.nome_projeto}" cadastrado',
            usuario=engenheiro,
            referencia_tipo='projeto',
            referencia_id=str(projeto.id_projeto),
            criado_em=projeto.criado_em,
        )
        if projeto.status != 'Pendente':
            template = MENSAGEM_POR_STATUS.get(projeto.status)
            if template:
                Notificacao.objects.create(
                    tipo=TIPO_POR_STATUS.get(projeto.status, 'info'),
                    mensagem=template.format(nome=projeto.nome_projeto),
                    usuario=engenheiro,
                    referencia_tipo='projeto',
                    referencia_id=str(projeto.id_projeto),
                    criado_em=projeto.atualizado_em,
                )

    try:
        from apps.normas.models import Norma

        for norma in Norma.objects.order_by('-criado_em')[:5]:
            Notificacao.objects.create(
                tipo='info',
                mensagem=f'Norma {norma.codigo} disponível no sistema',
                usuario='Sistema',
                referencia_tipo='norma',
                referencia_id=str(norma.id_norma),
                criado_em=norma.criado_em,
            )
    except Exception:
        pass

    registrar_projetos_atrasados()
