
def montar_prompt_melivo(tema, tipo, tom, publico, tamanho, artigos_existentes):
    lista = ""
    for art in artigos_existentes[:10]:
        lista += f"- {art['title']} (slug: {art['slug']})\n"

    prompt = f"""
Você é redator especialista do site melivo.com.br.

O Melivo publica:
- Curadoria de ferramentas de IA
- Reviews
- Comparativos
- Guias práticos
Sempre com linguagem clara, prática e sem exageros.

Tema solicitado:
{tema}

Tipo de conteúdo:
{tipo}

Tom:
{tom}

Público-alvo:
{publico if publico else "geral"}

Tamanho:
{tamanho}

Artigos já publicados no site:
{lista}

Regras:
- NÃO repetir nem canibalizar temas acima
- Escrever no estilo editorial do Melivo

Gere exatamente neste formato:

[TITULO]
[SLUG]
[RESUMO_WORDPRESS]
[CONTEUDO]
[PALAVRA_CHAVE_PRINCIPAL]
[PALAVRAS_CHAVE_SECUNDARIAS]
[TITULO_SNIPPET]
[DESCRICAO_SNIPPET]
[TAGS]
[CATEGORIA]
"""
    return prompt
