import ezdxf
import json
import os
from pathlib import Path
from dataclasses import dataclass, field, asdict
from collections import defaultdict
from typing import Any

@dataclass
class EntidadeGeometrica:
    tipo: str
    layer: str
    dados: dict[str, Any]

@dataclass
class BlocoInserido:
    nome: str
    layer: str
    insercao: tuple[float, float, float]
    atributos: dict[str, str] = field(default_factory=dict)
    geometria_interna: list[dict] = field(default_factory=list)  

@dataclass
class TextoExtraido:
    conteudo: str
    layer: str
    posicao: tuple[float, float]
    tipo: str

@dataclass
class HatchExtraido:                                              
    layer: str
    area: float
    num_paths: int
    ponto_semente: tuple[float, float] | None

@dataclass
class DimensionExtraida:                                        
    layer: str
    valor_texto: str
    valor_medido: float | None
    ponto_definicao: tuple[float, float]
    ponto_texto: tuple[float, float] | None

@dataclass
class LeaderExtraido:                                            
    layer: str
    tipo: str   
    texto: str
    vertices: list[tuple[float, float]]

@dataclass
class ResultadoExtracao:
    arquivo: str
    layers: list[str]
    entidades: list[EntidadeGeometrica]
    blocos: list[BlocoInserido]
    textos: list[TextoExtraido]
    hatches: list[HatchExtraido] = field(default_factory=list)          
    dimensions: list[DimensionExtraida] = field(default_factory=list)  
    leaders: list[LeaderExtraido] = field(default_factory=list)       
    resumo: dict[str, int] = field(default_factory=dict)


class ExtratorDXF:
    ENTIDADES_GEOMETRICAS = {"LINE","CIRCLE","ARC","ELLIPSE","LWPOLYLINE","POLYLINE","SPLINE","POINT","SOLID","HATCH"}

    def __init__(self, caminho: str):
        self.caminho = caminho
        self.doc = None
        self.msp = None

    def carregar(self) -> bool:
        try:
            self.doc = ezdxf.readfile(self.caminho)
            self.msp = self.doc.modelspace()
            print(f"Arquivo carregado: {self.caminho}")
            return True
        except Exception as e:
            print(f"Falha ao carregar DXF: {e}")
            return False

    def extrair_layers(self) -> list[str]:
        return [layer.dxf.name for layer in self.doc.layers]

    def _extrair_line(self,e): return {"inicio":tuple(round(v,4) for v in e.dxf.start), "fim":tuple(round(v,4) for v in e.dxf.end), "comprimento":round(e.dxf.start.distance(e.dxf.end),4)}
    def _extrair_circle(self,e): return {"centro":tuple(round(v,4) for v in e.dxf.center),"raio":round(e.dxf.radius,4)}
    def _extrair_arc(self,e): return {"centro":tuple(round(v,4) for v in e.dxf.center),"raio":round(e.dxf.radius,4),"angulo_inicio":round(e.dxf.start_angle,4),"angulo_fim":round(e.dxf.end_angle,4)}
    def _extrair_lwpolyline(self,e): pontos=[(round(p[0],4),round(p[1],4)) for p in e.get_points()]; return {"pontos":pontos,"fechada":e.closed,"num_pontos":len(pontos)}
    def _extrair_polyline(self,e): pontos=[(round(v.dxf.location.x,4),round(v.dxf.location.y,4),round(v.dxf.location.z,4)) for v in e.vertices]; return {"pontos":pontos,"fechada":bool(e.dxf.flags&1),"num_pontos":len(pontos)}
    def _extrair_spline(self,e): pontos=[(round(p[0],4),round(p[1],4)) for p in e.control_points]; return {"grau":e.dxf.degree,"pontos_controle":pontos,"num_pontos":len(pontos)}
    def _extrair_ellipse(self,e): return {"centro":tuple(round(v,4) for v in e.dxf.center),"eixo_maior":tuple(round(v,4) for v in e.dxf.major_axis),"razao":round(e.dxf.ratio,4)}
    def _extrair_point(self,e): return {"posicao":tuple(round(v,4) for v in e.dxf.location)}

    _EXTRATORES = {
        "LINE": _extrair_line,"CIRCLE": _extrair_circle,"ARC": _extrair_arc,
        "LWPOLYLINE": _extrair_lwpolyline,"POLYLINE": _extrair_polyline,
        "SPLINE": _extrair_spline,"ELLIPSE": _extrair_ellipse,"POINT": _extrair_point
    }

    def extrair_entidades(self) -> list[EntidadeGeometrica]:
        entidades=[]
        for e in self.msp:
            tipo=e.dxftype()
            if tipo not in self.ENTIDADES_GEOMETRICAS: continue
            layer=e.dxf.get("layer","0")
            extrator=self._EXTRATORES.get(tipo)
            if extrator:
                try: entidades.append(EntidadeGeometrica(tipo=tipo,layer=layer,dados=extrator(self,e)))
                except: pass
        return entidades

    #extrai geometria interna de um bloco 
    def _extrair_geometria_bloco(self, nome_bloco: str) -> list[dict]:
        if nome_bloco not in self.doc.blocks:
            return []
        geometria = []
        for e in self.doc.blocks[nome_bloco]:
            tipo = e.dxftype()
            extrator = self._EXTRATORES.get(tipo)
            if extrator:
                try:
                    geometria.append({
                        "tipo": tipo,
                        "layer": e.dxf.get("layer", "0"),
                        "dados": extrator(self, e)
                    })
                except:
                    pass
            elif tipo == "INSERT":  
                try:
                    sub = self._extrair_geometria_bloco(e.dxf.name)
                    geometria.extend(sub)
                except:
                    pass
        return geometria

    def extrair_blocos(self) -> list[BlocoInserido]:
        blocos = []
        for e in self.msp.query("INSERT"):
            nome  = e.dxf.name
            layer = e.dxf.get("layer", "0")
            ins   = e.dxf.insert
            atributos = {
                attrib.dxf.tag.strip().upper(): attrib.dxf.text.strip()
                for attrib in e.attribs
                if attrib.dxf.tag.strip() and attrib.dxf.text.strip()
            }
            geometria_interna = self._extrair_geometria_bloco(nome)  
            blocos.append(BlocoInserido(
                nome=nome, layer=layer,
                insercao=(round(ins.x,4), round(ins.y,4), round(ins.z,4)),
                atributos=atributos,
                geometria_interna=geometria_interna                   
            ))
        return blocos

    def extrair_textos(self) -> list[TextoExtraido]:
        textos=[]
        for tipo_query in ["TEXT","MTEXT","ATTRIB"]:
            for e in self.msp.query(tipo_query):
                try:
                    layer=e.dxf.get("layer","0")
                    conteudo=e.text.strip() if tipo_query=="MTEXT" else e.dxf.text.strip()
                    pos=e.dxf.insert
                    if conteudo: textos.append(TextoExtraido(conteudo=conteudo,layer=layer,posicao=(round(pos.x,4),round(pos.y,4)),tipo=tipo_query))
                except: pass
        return textos

    def extrair_hatches(self) -> list[HatchExtraido]:
        hatches = []
        for e in self.msp.query("HATCH"):
            try:
                layer = e.dxf.get("layer", "0")
                area  = round(e.dxf.get("area", 0.0), 4)
                num_paths = len(e.paths)
                semente = None
                if e.seeds:
                    s = e.seeds[0]
                    semente = (round(s[0], 4), round(s[1], 4))
                hatches.append(HatchExtraido(layer=layer, area=area, num_paths=num_paths, ponto_semente=semente))
            except:
                pass
        return hatches

    def extrair_dimensions(self) -> list[DimensionExtraida]:
        dimensions = []
        for e in self.msp.query("DIMENSION"):
            try:
                layer       = e.dxf.get("layer", "0")
                valor_texto = e.dxf.get("text", "")
                valor_medido = None
                try: valor_medido = round(e.dxf.actual_measurement, 4)
                except: pass
                defpt  = e.dxf.defpoint
                ponto_def = (round(defpt.x, 4), round(defpt.y, 4))
                ponto_txt = None
                try:
                    tpt = e.dxf.text_midpoint
                    ponto_txt = (round(tpt.x, 4), round(tpt.y, 4))
                except:
                    pass
                dimensions.append(DimensionExtraida(
                    layer=layer, valor_texto=valor_texto,
                    valor_medido=valor_medido,
                    ponto_definicao=ponto_def, ponto_texto=ponto_txt
                ))
            except:
                pass
        return dimensions

    def extrair_leaders(self) -> list[LeaderExtraido]:
        leaders = []

        for e in self.msp.query("LEADER"):
            try:
                layer    = e.dxf.get("layer", "0")
                vertices = [(round(v[0], 4), round(v[1], 4)) for v in e.vertices]
                texto    = ""
                try: texto = e.dxf.text.strip()
                except: pass
                leaders.append(LeaderExtraido(layer=layer, tipo="LEADER", texto=texto, vertices=vertices))
            except:
                pass

        for e in self.msp.query("MLEADER"):
            try:
                layer    = e.dxf.get("layer", "0")
                texto    = ""
                vertices = []
                try: texto = e.context.mtext.insert.strip() if e.context.mtext else ""
                except: pass
                try:
                    for lline in e.context.leaders:
                        for spine in lline.lines:
                            vertices += [(round(p[0], 4), round(p[1], 4)) for p in spine.vertices]
                except:
                    pass
                leaders.append(LeaderExtraido(layer=layer, tipo="MLEADER", texto=texto, vertices=vertices))
            except:
                pass

        return leaders

    def extrair(self) -> ResultadoExtracao | None:
        if not self.carregar(): return None
        layers     = self.extrair_layers()
        entidades  = self.extrair_entidades()
        blocos     = self.extrair_blocos()
        textos     = self.extrair_textos()
        hatches    = self.extrair_hatches()      
        dimensions = self.extrair_dimensions()   
        leaders    = self.extrair_leaders()      

        resumo = {
            "total_layers": len(layers),
            "total_entidades": len(entidades),
            "total_blocos": len(blocos),
            "total_textos": len(textos),
            "total_hatches": len(hatches),         
            "total_dimensions": len(dimensions),   
            "total_leaders": len(leaders),         
            "entidades_por_tipo": defaultdict(int)
        }
        for ent in entidades: resumo["entidades_por_tipo"][ent.tipo] += 1
        resumo["entidades_por_tipo"] = dict(resumo["entidades_por_tipo"])

        return ResultadoExtracao(
            arquivo=self.caminho, layers=layers, entidades=entidades,
            blocos=blocos, textos=textos,
            hatches=hatches, dimensions=dimensions, leaders=leaders,  
            resumo=resumo
        )


class GeradorChunksDXF:
    def __init__(self, resultado: ResultadoExtracao):
        self.r=resultado
        self.nome_arquivo=Path(resultado.arquivo).stem

    def chunk_resumo_geral(self): r=self.r.resumo; layers_str=", ".join(self.r.layers[:20]); tipos_str=", ".join(f"{k}: {v}" for k,v in r.get("entidades_por_tipo",{}).items()); return f"Planta elétrica: {self.nome_arquivo}\nLayers: {layers_str}\nTotal entidades: {r['total_entidades']}\nTipos: {tipos_str}\nBlocos: {r['total_blocos']}\nTextos: {r['total_textos']}"

    def chunks_por_layer(self):
        por_layer=defaultdict(list)
        for ent in self.r.entidades: por_layer[ent.layer].append(ent)
        chunks=[]
        for layer,ents in por_layer.items():
            tipos=defaultdict(int)
            for e in ents: tipos[e.tipo]+=1
            tipos_str=", ".join(f"{k}: {v}" for k,v in tipos.items())
            chunks.append(f"Layer '{layer}' da planta {self.nome_arquivo}:\n  Entidades: {tipos_str}\n  Total: {len(ents)} entidades")
        return chunks

    def chunks_blocos(self):
        chunks=[]
        for b in self.r.blocos:
            attrs=""
            if b.atributos: attrs="\n  Atributos:\n"+"".join(f"    {k}: {v}\n" for k,v in b.atributos.items())
            geo_resumo = ""
            if b.geometria_interna:
                contagem = defaultdict(int)
                for g in b.geometria_interna: contagem[g["tipo"]] += 1
                geo_resumo = "\n  Geometria interna: " + ", ".join(f"{k}: {v}" for k,v in contagem.items())
            chunks.append(f"Componente '{b.nome}' na planta {self.nome_arquivo}:\n  Layer: {b.layer}\n  Posição: x={b.insercao[0]}, y={b.insercao[1]}, z={b.insercao[2]}{attrs}{geo_resumo}")
        return chunks

    def chunks_textos_por_layer(self):
        por_layer=defaultdict(list)
        for t in self.r.textos: por_layer[t.layer].append(t)
        chunks=[]
        for layer,textos in por_layer.items():
            conteudos="\n".join(f"  [{t.tipo}] ({t.posicao[0]},{t.posicao[1]}): {t.conteudo}" for t in textos)
            chunks.append(f"Textos no layer '{layer}' da planta {self.nome_arquivo}:\n{conteudos}")
        return chunks

    def chunks_geometria_agrupada(self,max_por_chunk=50):
        chunks=[]
        buffer=[]
        for ent in self.r.entidades:
            buffer.append(f"[{ent.tipo}] layer={ent.layer} | {json.dumps(ent.dados,ensure_ascii=False)}")
            if len(buffer)>=max_por_chunk:
                chunks.append(f"Geometria {self.nome_arquivo} (fragmento):\n"+"\n".join(buffer))
                buffer=[]
        if buffer: chunks.append(f"Geometria {self.nome_arquivo} (fragmento):\n"+"\n".join(buffer))
        return chunks

    def chunks_hatches(self):
        if not self.r.hatches: return []
        por_layer = defaultdict(list)
        for h in self.r.hatches: por_layer[h.layer].append(h)
        chunks = []
        for layer, hs in por_layer.items():
            area_total = round(sum(h.area for h in hs), 4)
            linhas = "\n".join(
                f"  área={h.area}m² | paths={h.num_paths} | semente={h.ponto_semente}" for h in hs
            )
            chunks.append(f"Hatches no layer '{layer}' da planta {self.nome_arquivo}:\n  Área total: {area_total}m²\n{linhas}")
        return chunks

    def chunks_dimensions(self):
        if not self.r.dimensions: return []
        por_layer = defaultdict(list)
        for d in self.r.dimensions: por_layer[d.layer].append(d)
        chunks = []
        for layer, dims in por_layer.items():
            linhas = "\n".join(
                f"  texto='{d.valor_texto}' | medido={d.valor_medido}m | def={d.ponto_definicao}"
                for d in dims
            )
            chunks.append(f"Cotas no layer '{layer}' da planta {self.nome_arquivo}:\n{linhas}")
        return chunks

    def chunks_leaders(self):
        if not self.r.leaders: return []
        linhas = "\n".join(
            f"  [{l.tipo}] layer={l.layer} | texto='{l.texto}' | vertices={l.vertices[:2]}..."
            for l in self.r.leaders
        )
        return [f"Leaders/MLeaders da planta {self.nome_arquivo}:\n{linhas}"]

    def gerar_todos_chunks(self, incluir_geometria=True):
        print("Dividindo dados em chunks...")
        chunks = [self.chunk_resumo_geral()]
        chunks.extend(self.chunks_por_layer())
        chunks.extend(self.chunks_blocos())
        chunks.extend(self.chunks_textos_por_layer())
        chunks.extend(self.chunks_hatches())      
        chunks.extend(self.chunks_dimensions())
        chunks.extend(self.chunks_leaders())      
        if incluir_geometria: chunks.extend(self.chunks_geometria_agrupada())
        return chunks


def processar_dxf_para_json(dxf_path_or_obj: Any, gerar_chunks=True) -> dict:
    extrator=ExtratorDXF(dxf_path_or_obj if isinstance(dxf_path_or_obj,str) else "DXF_EM_MEMORIA")
    resultado=extrator.extrair()
    if resultado is None: raise ValueError("Falha na extração do DXF")
    if gerar_chunks:
        gerador=GeradorChunksDXF(resultado)
        chunks=gerador.gerar_todos_chunks()
        resultado_dict=asdict(resultado)
        resultado_dict["chunks"]=chunks
        print("Chunks gerados com sucesso.")
    else:
        resultado_dict=asdict(resultado)
    return resultado_dict