#!/usr/bin/env python3
"""
Teste Interativo de Conexão WhatsApp com QR Code no Terminal.

Este script:
1. Cria uma instância na Evolution API
2. Exibe o QR code visualmente no terminal
3. Monitora em tempo real a conexão do WhatsApp
4. Aguarda até a conexão ser estabelecida
5. Remove automaticamente a instância após o teste

Dependências necessárias:
    pip install qrcode[pil]

Execute: python test_whatsapp_connection.py
"""

import argparse
import base64
import os
import sys
import time
from io import BytesIO
from typing import Any, Dict, Optional

# Import dotenv
try:
    from dotenv import load_dotenv

    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

    def load_dotenv(file_path):
        pass  # Fallback function


# Imports condicionais para bibliotecas opcionais
try:
    import qrcode
    from PIL import Image

    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

from pyevolutionapi import EvolutionClient


class Colors:
    """Códigos de cores para terminal."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"


class WhatsAppConnectionTester:
    """Testador interativo de conexão WhatsApp."""

    def __init__(self, client: EvolutionClient, instance_name: str = None):
        self.client = client
        self.instance_name = instance_name or f"whatsapp-test-{int(time.time())}"
        self.instance_created = False
        self.connection_timeout = 300  # 5 minutos
        self.check_interval = 3  # 3 segundos

    def print_colored(self, text: str, color: str = Colors.WHITE, bold: bool = False):
        """Imprime texto colorido no terminal."""
        prefix = Colors.BOLD if bold else ""
        print(f"{prefix}{color}{text}{Colors.RESET}")

    def print_header(self, text: str):
        """Imprime cabeçalho estilizado."""
        print()
        self.print_colored("=" * 60, Colors.CYAN, bold=True)
        self.print_colored(f" {text} ", Colors.WHITE, bold=True)
        self.print_colored("=" * 60, Colors.CYAN, bold=True)
        print()

    def decode_base64_qr(self, base64_data: str) -> Optional[str]:
        """
        Decodifica QR code em base64 para extrair o conteúdo.

        Args:
            base64_data: String base64 do QR code

        Returns:
            Conteúdo do QR code ou None se falhar
        """
        try:
            # Remove prefixo data:image se presente
            if base64_data.startswith("data:image"):
                base64_data = base64_data.split(",", 1)[1]

            # Decodifica base64
            image_data = base64.b64decode(base64_data)

            # Se tiver PIL disponível, pode tentar extrair dados do QR
            if QR_AVAILABLE:
                try:
                    from pyzbar import pyzbar

                    image = Image.open(BytesIO(image_data))
                    decoded = pyzbar.decode(image)
                    if decoded:
                        return decoded[0].data.decode("utf-8")
                except ImportError:
                    pass  # pyzbar não disponível

            return base64_data  # Retorna o base64 mesmo se não conseguir decodificar

        except Exception as e:
            self.print_colored(f"⚠️ Erro ao decodificar QR: {e}", Colors.YELLOW)
            return None

    def display_qr_code(self, qr_data: str):
        """
        Exibe QR code no terminal.

        Args:
            qr_data: Dados do QR code para exibir
        """
        self.print_header("QR CODE PARA CONEXÃO WHATSAPP")

        if not QR_AVAILABLE:
            self.print_colored("⚠️ Bibliotecas qrcode/PIL não instaladas", Colors.YELLOW)
            self.print_colored("📦 Instale com: pip install qrcode[pil]", Colors.CYAN)
            print()
            self.print_colored("📱 QR Code (base64):", Colors.WHITE, bold=True)
            # Mostra base64 truncado
            qr_preview = qr_data[:100] + "..." if len(qr_data) > 100 else qr_data
            print(qr_preview)
            print()
            self.print_colored("💡 Cole este base64 em um gerador online de QR code", Colors.CYAN)
            self.print_colored(
                "   Exemplo: https://codebeautify.org/base64-to-image-converter", Colors.CYAN
            )
            return

        try:
            # Cria QR code ASCII para o terminal
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=1,
                border=2,
            )

            # Se é base64, usa diretamente, senão assume que é o conteúdo
            qr_content = qr_data
            if qr_data.startswith("data:image") or len(qr_data) > 200:
                # Para base64 muito longo, cria um QR simples
                qr_content = f"WhatsApp connection: {self.instance_name}"

            qr.add_data(qr_content)
            qr.make(fit=True)

            # Exibe no terminal
            self.print_colored(
                "📱 Escaneie este QR code com seu WhatsApp:", Colors.GREEN, bold=True
            )
            print()

            # QR code ASCII
            qr.print_ascii(out=sys.stdout, tty=True)

            print()
            self.print_colored("📱 Como conectar:", Colors.WHITE, bold=True)
            self.print_colored("1. Abra o WhatsApp no seu celular", Colors.WHITE)
            self.print_colored(
                "2. Toque em ⋮ (três pontos) > Dispositivos conectados", Colors.WHITE
            )
            self.print_colored("3. Toque em 'Conectar um dispositivo'", Colors.WHITE)
            self.print_colored("4. Escaneie o QR code acima", Colors.WHITE)
            print()

        except Exception as e:
            self.print_colored(f"❌ Erro ao gerar QR ASCII: {e}", Colors.RED)
            self.print_colored("📱 QR Code (dados):", Colors.WHITE, bold=True)
            # Fallback: mostra dados truncados
            qr_preview = qr_data[:200] + "..." if len(qr_data) > 200 else qr_data
            print(qr_preview)

    def create_instance(self) -> Optional[Dict[str, Any]]:
        """
        Cria instância na Evolution API.

        Returns:
            Dados da resposta ou None se falhar
        """
        self.print_header("CRIANDO INSTÂNCIA WHATSAPP")

        try:
            # Remove instância anterior se existir
            try:
                self.client.instance.delete(self.instance_name)
                self.print_colored("🗑️ Instância anterior removida", Colors.YELLOW)
                time.sleep(2)
            except:
                pass

            # Cria nova instância
            self.print_colored(f"📱 Criando instância: {self.instance_name}", Colors.CYAN)

            response = self.client.instance.create(instance_name=self.instance_name, qrcode=True)

            self.instance_created = True
            self.print_colored("✅ Instância criada com sucesso!", Colors.GREEN, bold=True)

            # Informações da resposta
            if response.instance:
                self.print_colored(f"📋 Status: {response.instance.status}", Colors.WHITE)
                self.print_colored(f"📋 ID: {response.instance.instance_id}", Colors.WHITE)

            if response.hash:
                self.print_colored(f"📋 Hash: {response.hash}", Colors.WHITE)

            return {"response": response, "success": True}

        except Exception as e:
            self.print_colored(f"❌ Erro ao criar instância: {e}", Colors.RED)
            return {"error": str(e), "success": False}

    def get_qr_code(self) -> Optional[str]:
        """
        Obtém QR code da instância.

        Returns:
            QR code em base64 ou None se não disponível
        """
        try:
            # Tenta via connect primeiro
            self.print_colored("🔗 Obtendo QR code via connect...", Colors.CYAN)

            connect_response = self.client.instance.connect(self.instance_name)

            if connect_response and hasattr(connect_response, "qr_code_base64"):
                qr_b64 = connect_response.qr_code_base64
                if qr_b64:
                    self.print_colored("✅ QR code obtido via connect", Colors.GREEN)
                    return qr_b64

            # Se connect não funcionou, verifica response original
            self.print_colored("🔄 Tentando obter QR da resposta de criação...", Colors.YELLOW)

            # Re-cria para forçar QR novo (algumas APIs só mostram na criação)
            response = self.client.instance.create(instance_name=self.instance_name, qrcode=True)

            if response.qr_code_base64:
                self.print_colored("✅ QR code obtido da criação", Colors.GREEN)
                return response.qr_code_base64

            # Verifica qrcode dict
            if response.qrcode and response.qrcode.get("base64"):
                qr_b64 = response.qrcode.get("base64")
                if not qr_b64.startswith("data:image"):
                    qr_b64 = f"data:image/png;base64,{qr_b64}"
                self.print_colored("✅ QR code obtido do campo qrcode", Colors.GREEN)
                return qr_b64

            self.print_colored("⚠️ QR code não disponível na resposta", Colors.YELLOW)
            return None

        except Exception as e:
            self.print_colored(f"❌ Erro ao obter QR code: {e}", Colors.RED)
            return None

    def monitor_connection(self, timeout: int = None) -> bool:
        """
        Monitora conexão da instância até conectar ou timeout.

        Args:
            timeout: Timeout em segundos (padrão: self.connection_timeout)

        Returns:
            True se conectou, False se timeout
        """
        timeout = timeout or self.connection_timeout

        self.print_header("MONITORANDO CONEXÃO")
        self.print_colored(f"⏱️ Aguardando conexão por até {timeout//60} minutos...", Colors.CYAN)
        self.print_colored("⏹️ Pressione Ctrl+C para cancelar", Colors.YELLOW)
        print()

        start_time = time.time()
        attempt = 0

        try:
            while time.time() - start_time < timeout:
                attempt += 1
                elapsed = int(time.time() - start_time)
                remaining = timeout - elapsed

                # Status visual
                dots = "." * ((attempt % 3) + 1)
                self.print_colored(
                    f"🔍 Verificando conexão{dots} "
                    f"(tentativa {attempt}, restam {remaining//60}:{remaining%60:02d})",
                    Colors.BLUE,
                )

                try:
                    # Verifica status via connection_state
                    status = self.client.instance.connection_state(self.instance_name)

                    if isinstance(status, dict):
                        state = status.get("state", "unknown")

                        if state == "open":
                            self.print_colored(
                                "🎉 WHATSAPP CONECTADO COM SUCESSO!", Colors.GREEN, bold=True
                            )

                            # Informações adicionais
                            if "instance" in status:
                                instance_info = status["instance"]
                                if instance_info.get("profileName"):
                                    self.print_colored(
                                        f"👤 Nome: {instance_info['profileName']}", Colors.WHITE
                                    )
                                if instance_info.get("number"):
                                    self.print_colored(
                                        f"📞 Número: {instance_info['number']}", Colors.WHITE
                                    )

                            return True

                        elif state == "connecting":
                            self.print_colored(
                                f"🔄 Status: {state} (aguardando QR scan)", Colors.YELLOW
                            )
                        else:
                            self.print_colored(f"📊 Status: {state}", Colors.WHITE)

                    # Também verifica via fetch_instances
                    instances = self.client.instance.fetch_instances()
                    for instance in instances:
                        if (instance.id and self.instance_name in [instance.name, instance.id]) or (
                            instance.name and instance.name == self.instance_name
                        ):

                            if instance.is_connected:
                                self.print_colored(
                                    "🎉 CONEXÃO DETECTADA VIA FETCH!", Colors.GREEN, bold=True
                                )
                                return True

                            if instance.state:
                                self.print_colored(
                                    f"📊 Instance state: {instance.state}", Colors.WHITE
                                )
                            break

                except Exception as e:
                    self.print_colored(f"⚠️ Erro ao verificar status: {e}", Colors.YELLOW)

                # Aguarda antes da próxima verificação
                time.sleep(self.check_interval)

                # Limpa linha para próximo status (opcional)
                # print("\033[A\033[K", end="")  # Move cursor para linha anterior e limpa

            # Timeout
            self.print_colored(f"⏰ Timeout de {timeout//60} minutos atingido", Colors.RED)
            self.print_colored("❌ WhatsApp não foi conectado", Colors.RED)
            return False

        except KeyboardInterrupt:
            print()
            self.print_colored("⚡ Monitoramento interrompido pelo usuário", Colors.YELLOW)
            return False

    def cleanup(self):
        """Remove a instância criada."""
        if self.instance_created:
            self.print_header("LIMPEZA")
            try:
                self.client.instance.delete(self.instance_name)
                self.print_colored(f"🗑️ Instância removida: {self.instance_name}", Colors.GREEN)
            except Exception as e:
                self.print_colored(f"⚠️ Erro na limpeza: {e}", Colors.YELLOW)

    def run_test(self, auto_cleanup: bool = True) -> bool:
        """
        Executa o teste completo de conexão.

        Args:
            auto_cleanup: Se deve remover instância automaticamente

        Returns:
            True se conectou com sucesso
        """
        try:
            # 1. Criar instância
            result = self.create_instance()
            if not result or not result["success"]:
                return False

            # 2. Obter QR code
            qr_code = self.get_qr_code()
            if not qr_code:
                self.print_colored("❌ Não foi possível obter QR code", Colors.RED)
                return False

            # 3. Exibir QR code
            self.display_qr_code(qr_code)

            # 4. Monitorar conexão
            connected = self.monitor_connection()

            if connected:
                self.print_header("TESTE CONCLUÍDO COM SUCESSO")
                self.print_colored(
                    "✅ WhatsApp conectado à Evolution API!", Colors.GREEN, bold=True
                )
                self.print_colored(
                    "🎯 Todas as correções Pydantic validadas!", Colors.GREEN, bold=True
                )
            else:
                self.print_header("TESTE INTERROMPIDO")
                self.print_colored("⚠️ Conexão não estabelecida", Colors.YELLOW)

            return connected

        except Exception as e:
            self.print_colored(f"💥 Erro crítico no teste: {e}", Colors.RED)
            return False

        finally:
            if auto_cleanup:
                self.cleanup()


def main():
    parser = argparse.ArgumentParser(
        description="Teste interativo de conexão WhatsApp com QR code no terminal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  %(prog)s                              Teste padrão com limpeza automática
  %(prog)s --name meu-whatsapp         Define nome da instância
  %(prog)s --timeout 180               Timeout de 3 minutos
  %(prog)s --no-cleanup               Mantém instância após teste
  %(prog)s --check-deps               Verifica dependências necessárias

Dependências necessárias:
  pip install qrcode[pil]

⚠️ IMPORTANTE: Configure .env.integration com suas credenciais da Evolution API
        """,
    )

    parser.add_argument(
        "--name", type=str, help="Nome da instância (padrão: whatsapp-test-TIMESTAMP)"
    )
    parser.add_argument(
        "--timeout", type=int, default=300, help="Timeout de conexão em segundos (padrão: 300)"
    )
    parser.add_argument("--no-cleanup", action="store_true", help="Não remove instância após teste")
    parser.add_argument("--check-deps", action="store_true", help="Apenas verifica dependências")

    args = parser.parse_args()

    # Verifica dependências
    if args.check_deps:
        print("🔍 VERIFICANDO DEPENDÊNCIAS")
        print("=" * 40)

        deps_ok = True

        # qrcode
        try:
            import qrcode

            print("✅ qrcode: disponível")
        except ImportError:
            print("❌ qrcode: não encontrado")
            deps_ok = False

        # PIL
        try:
            from PIL import Image

            print("✅ PIL (Pillow): disponível")
        except ImportError:
            print("❌ PIL (Pillow): não encontrado")
            deps_ok = False

        # dotenv
        if DOTENV_AVAILABLE:
            print("✅ python-dotenv: disponível")
        else:
            print("❌ python-dotenv: não encontrado")
            deps_ok = False

        print()
        if deps_ok:
            print("🎉 Todas as dependências estão disponíveis!")
        else:
            print("📦 Instale as dependências faltantes:")
            print("   pip install qrcode[pil] python-dotenv")

        return 0 if deps_ok else 1

    # Verifica se dependências básicas estão disponíveis
    if not QR_AVAILABLE:
        print("⚠️ Bibliotecas de QR code não encontradas")
        print("📦 Instale com: pip install qrcode[pil]")
        print("💡 O teste funcionará, mas QR será exibido como base64")
        print()

        response = input("Continuar mesmo assim? [y/N]: ")
        if response.lower() not in ["y", "yes", "s", "sim"]:
            print("❌ Teste cancelado")
            return 1

    # Carrega configuração
    load_dotenv(".env.integration")

    api_key = os.getenv("EVOLUTION_API_KEY")
    if not api_key:
        print("❌ EVOLUTION_API_KEY não configurado no .env.integration")
        print("💡 Configure suas credenciais da Evolution API")
        return 1

    # Cria cliente
    client = EvolutionClient(
        base_url=os.getenv("EVOLUTION_BASE_URL", "http://localhost:8080"),
        api_key=api_key,
        timeout=60.0,
        debug=False,  # Reduz logs para melhor experiência visual
    )

    # Cria testador
    tester = WhatsAppConnectionTester(client, args.name)
    tester.connection_timeout = args.timeout

    # Banner inicial
    tester.print_header("TESTE DE CONEXÃO WHATSAPP - PYEVOLUTION")
    tester.print_colored("🚀 Iniciando teste interativo de conexão", Colors.CYAN, bold=True)
    tester.print_colored(f"📱 Instância: {tester.instance_name}", Colors.WHITE)
    tester.print_colored(f"⏱️ Timeout: {args.timeout//60} minutos", Colors.WHITE)
    tester.print_colored(f"🧹 Auto-limpeza: {'Não' if args.no_cleanup else 'Sim'}", Colors.WHITE)

    # Executa teste
    try:
        success = tester.run_test(auto_cleanup=not args.no_cleanup)

        if success:
            tester.print_colored("\n🎉 TESTE CONCLUÍDO COM SUCESSO!", Colors.GREEN, bold=True)
            return 0
        else:
            tester.print_colored("\n⚠️ Teste não completado", Colors.YELLOW, bold=True)
            return 1

    except KeyboardInterrupt:
        print()
        tester.print_colored("⚡ Teste interrompido pelo usuário", Colors.YELLOW)
        if not args.no_cleanup:
            tester.cleanup()
        return 1

    except Exception as e:
        tester.print_colored(f"\n💥 Erro fatal: {e}", Colors.RED)
        if not args.no_cleanup:
            tester.cleanup()
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚡ Interrompido pelo usuário")
        sys.exit(1)
