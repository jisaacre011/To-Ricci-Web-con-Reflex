import reflex as rx

# --- Paleta de Colores ---
CREAM      = "#FAF7F2"
CREAM_DARK = "#F0EBE1"
INK        = "#1C1C1A"
TAUPE      = "#8A7E72"
GOLD       = "#B8975A"
WHITE      = "#FFFFFF"
WARM_GRAY  = "#E8E2D9"

# --- Base de datos simulada de productos ---
PRODUCTS_INFO: dict = {
    "01": {"name": "Santiago",  "price": 18500, "price_display": "RD$ 18,500"},
    "02": {"name": "Bangkok",   "price":  9800, "price_display": "RD$  9,800"},
    "03": {"name": "Tokio",     "price": 12200, "price_display": "RD$ 12,200"},
    "04": {"name": "Lisboa",    "price": 24000, "price_display": "RD$ 24,000"},
}

# --- Estado Global de la Aplicación ---
class PageState(rx.State):
    selected_sizes: dict[str, str]  = {"01": "", "02": "", "03": "", "04": ""}
    added: dict[str, bool]          = {"01": False, "02": False, "03": False, "04": False}
    # Lista de items en carrito: [id, product_id, name, size, price, price_display]
    cart_items: list[list[str]]     = []
    cart_open: bool                 = False
    next_id: int                    = 0

    @rx.var
    def cart_count(self) -> int:
        return len(self.cart_items)

    @rx.var
    def cart_is_empty(self) -> bool:
        return len(self.cart_items) == 0

    @rx.var
    def cart_total(self) -> str:
        # Sumamos los precios (índice 4) y formateamos con comas
        total = sum(int(item[4]) for item in self.cart_items)
        return f"RD$ {total:,}"

    def set_size(self, product_id: str, size: str):
        self.selected_sizes[product_id] = size

    def add_to_cart(self, product_id: str):
        # Validamos que haya seleccionado una talla
        if not self.selected_sizes[product_id]:
            return rx.window_alert("Por favor, selecciona una talla antes de agregar al carrito.")

        info = PRODUCTS_INFO[product_id]
        
        # Creamos el nuevo item y lo agregamos a la lista
        new_item = [
            str(self.next_id),
            product_id,
            info["name"],
            self.selected_sizes[product_id],
            str(info["price"]),
            info["price_display"]
        ]
        self.cart_items.append(new_item)
        self.added[product_id] = True
        self.next_id += 1

    def remove_from_cart(self, item_id: str):
        item_id_int = int(item_id)
        self.cart_items = [i for i in self.cart_items if int(i[0]) != item_id_int]

    def reset_added(self, product_id: str):
        self.added[product_id] = False
        self.selected_sizes[product_id] = "" # Limpiamos la talla al seguir comprando

    def toggle_cart(self):
        self.cart_open = not self.cart_open

    def close_cart(self):
        self.cart_open = False


# --- Componentes de UI ---

def cart_item_row(item: list[str]) -> rx.Component:
    """Renderiza una fila individual dentro del carrito de compras."""
    item_id, _, name, size, _, price_display = item[0], item[1], item[2], item[3], item[4], item[5]
    
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text(name, font_family="'Cormorant Garamond', serif", font_size="1.15rem", font_weight="300", color=INK, letter_spacing="0.02em"),
                rx.hstack(
                    rx.text("Talla:", font_size="0.6rem", color=TAUPE, letter_spacing="0.15em", text_transform="uppercase"),
                    rx.text(size, font_size="0.6rem", color=TAUPE, letter_spacing="0.15em"),
                    gap="0.3rem",
                ),
                align="start", gap="0.25rem", flex="1",
            ),
            rx.vstack(
                rx.text(price_display, font_family="'Cormorant Garamond', serif", font_size="1rem", font_weight="300", color=INK, letter_spacing="0.03em"),
                rx.button(
                    "× Eliminar",
                    on_click=PageState.remove_from_cart(item_id),
                    background="transparent", color=TAUPE, font_size="0.58rem",
                    letter_spacing="0.12em", text_transform="uppercase",
                    padding="0", border="none", cursor="pointer",
                    _hover={"color": INK}, min_width="0",
                ),
                align="end", gap="0.4rem",
            ),
            width="100%", align="center",
        ),
        padding_y="1.2rem",
        border_bottom=f"1px solid {WARM_GRAY}",
        width="100%",
    )


def cart_sidebar() -> rx.Component:
    """Panel lateral desplegable para el carrito de compras."""
    return rx.cond(
        PageState.cart_open,
        rx.box(
            # Fondo oscuro borroso (Overlay)
            rx.box(
                on_click=PageState.close_cart,
                position="fixed", top="0", left="0", right="0", bottom="0",
                background="rgba(28,28,26,0.35)", z_index="1000",
                backdrop_filter="blur(2px)",
            ),
            # Panel lateral
            rx.box(
                rx.vstack(
                    # Cabecera del carrito
                    rx.hstack(
                        rx.hstack(
                            rx.text("Carrito", font_family="'Cormorant Garamond', serif", font_size="1.5rem", font_weight="300", color=INK, letter_spacing="0.08em"),
                            rx.cond(
                                PageState.cart_count > 0,
                                rx.box(
                                    rx.text(PageState.cart_count, font_size="0.58rem", color=WHITE, line_height="1"),
                                    background=GOLD, border_radius="999px", width="18px", height="18px",
                                    display="flex", align_items="center", justify_content="center",
                                ),
                            ),
                            gap="0.6rem", align="center",
                        ),
                        rx.button(
                            "✕", on_click=PageState.close_cart,
                            background="transparent", color=TAUPE, font_size="1rem",
                            padding="0.25rem", border="none", cursor="pointer",
                            _hover={"color": INK}, min_width="0",
                        ),
                        justify="between", align="center", width="100%",
                        padding_bottom="1.5rem", border_bottom=f"1px solid {WARM_GRAY}",
                    ),
                    
                    # Contenido del carrito
                    rx.cond(
                        PageState.cart_is_empty,
                        rx.vstack(
                            rx.box(height="3rem"),
                            rx.text("Tu carrito está vacío.", font_family="'Cormorant Garamond', serif", font_size="1.15rem", font_weight="300", color=TAUPE, font_style="italic", text_align="center"),
                            rx.text("Agrega piezas de la colección.", font_size="0.65rem", color=TAUPE, letter_spacing="0.1em", text_transform="uppercase", text_align="center", opacity="0.7", margin_top="0.5rem"),
                            align="center", width="100%",
                        ),
                        rx.vstack(
                            rx.foreach(PageState.cart_items, cart_item_row),
                            rx.box(height="0.5rem"),
                            rx.hstack(
                                rx.text("Subtotal", font_size="0.62rem", letter_spacing="0.3em", color=TAUPE, text_transform="uppercase"),
                                rx.text(PageState.cart_total, font_family="'Cormorant Garamond', serif", font_size="1.4rem", font_weight="300", color=INK),
                                justify="between", align="center", width="100%",
                                padding_y="1.5rem", border_top=f"1px solid {WARM_GRAY}",
                            ),
                            rx.button(
                                "Proceder al Pago",
                                background=INK, color=CREAM, border_radius="0", font_size="0.7rem",
                                letter_spacing="0.2em", text_transform="uppercase", padding="1.1rem",
                                cursor="pointer", width="100%", _hover={"background": GOLD}, transition="all 0.3s ease",
                            ),
                            rx.text("Envío e impuestos calculados al finalizar", font_size="0.58rem", color=TAUPE, letter_spacing="0.06em", text_align="center", opacity="0.6", margin_top="0.75rem"),
                            width="100%", gap="0", align="start",
                        ),
                    ),
                    width="100%", align="start", gap="0", padding="2rem", overflow_y="auto", height="100%",
                ),
                position="fixed", top="0", right="0", width=["100%", "420px"], height="100vh",
                background=WHITE, z_index="1001", box_shadow="-4px 0 40px rgba(0,0,0,0.12)",
            ),
        )
    )


def navbar() -> rx.Component:
    """Barra de navegación principal."""
    return rx.box(
        rx.hstack(
            rx.text("TO' RICCI", font_family="'Cormorant Garamond', serif", font_size="1rem", font_weight="400", letter_spacing="0.3em", color=INK),
            rx.hstack(
                rx.link("Colección", href="#coleccion", color=TAUPE, font_size="0.7rem", letter_spacing="0.18em", text_transform="uppercase", _hover={"color": GOLD}),
                rx.link("Manifesto", href="#nosotros",  color=TAUPE, font_size="0.7rem", letter_spacing="0.18em", text_transform="uppercase", _hover={"color": GOLD}),
                rx.link("Contacto",  href="#contacto",  color=TAUPE, font_size="0.7rem", letter_spacing="0.18em", text_transform="uppercase", _hover={"color": GOLD}),
                rx.button(
                    rx.hstack(
                        rx.text("Carrito", font_size="0.7rem", letter_spacing="0.18em", text_transform="uppercase", color=TAUPE),
                        rx.cond(
                            PageState.cart_count > 0,
                            rx.box(
                                rx.text(PageState.cart_count, font_size="0.55rem", color=WHITE, line_height="1"),
                                background=GOLD, border_radius="999px", width="17px", height="17px",
                                display="flex", align_items="center", justify_content="center",
                            ),
                        ),
                        gap="0.4rem", align="center",
                    ),
                    on_click=PageState.toggle_cart,
                    background="transparent", border="none", padding="0",
                    cursor="pointer", _hover={"opacity": "0.7"},
                ),
                gap="2.5rem", align="center",
            ),
            justify="between", align="center", width="100%", padding="1.8rem 4rem",
        ),
        position="fixed", top="0", left="0", right="0", z_index="999",
        background=f"{CREAM}F5", border_bottom=f"1px solid {WARM_GRAY}", backdrop_filter="blur(8px)",
    )


def hero() -> rx.Component:
    """Sección principal de bienvenida (Hero)."""
    titulo = "TO' RICCI"
    letras = [
        rx.el.span(letra, class_name="hero-letter", style={"animation_delay": f"{0.05 + i * 0.06}s"})
        for i, letra in enumerate(titulo)
    ]
    return rx.box(
        rx.vstack(
            rx.text("Milano — Colección N. 001", font_size="0.68rem", letter_spacing="0.45em", color=GOLD, text_transform="uppercase", margin_bottom="2rem"),
            rx.heading(*letras, class_name="hero-title", font_family="'Cormorant Garamond', serif", font_weight="300", font_size=["3rem", "5rem", "7.5rem"], letter_spacing="0.2em", color=INK, line_height="1"),
            rx.box(background=GOLD, height="1px", width="50px", margin_y="2.5rem"),
            rx.text("Dieci pezzi. Nessuno uguale.", font_family="'Cormorant Garamond', serif", font_size="1.25rem", font_weight="300", color=TAUPE, letter_spacing="0.08em", font_style="italic"),
            rx.box(height="3rem"),
            rx.link(
                rx.button(
                    "Descubrir la Colección",
                    background=INK, color=CREAM, font_size="0.7rem", letter_spacing="0.2em",
                    text_transform="uppercase", padding="1.1rem 3.5rem", border_radius="0",
                    _hover={"background": GOLD, "color": WHITE}, cursor="pointer", transition="all 0.4s ease",
                ),
                href="#coleccion",
            ),
            align="center", justify="center", width="100%",
            min_height="100vh", padding="2rem", padding_top="7rem",
        ),
        width="100%", background=f"radial-gradient(ellipse at 50% 30%, {GOLD}0A 0%, {CREAM} 55%)", id="inicio",
    )


def section_divider(label: str) -> rx.Component:
    """Línea divisoria elegante para separar secciones."""
    return rx.hstack(
        rx.box(flex="1", height="1px", background=WARM_GRAY),
        rx.text(label, font_size="0.62rem", letter_spacing="0.45em", color=TAUPE, text_transform="uppercase", padding_x="2.5rem", white_space="nowrap"),
        rx.box(flex="1", height="1px", background=WARM_GRAY),
        align="center", width="100%", padding_x="4rem", padding_y="5rem",
    )


def product_card(product_id: str, name: str, subtitle: str, price: str, image_url: str, reverse: bool = False) -> rx.Component:
    """Tarjeta individual de un producto."""
    sizes = ["XS", "S", "M", "L", "XL"]

    # --- MEJORA IMPORTANTE: Usamos rx.image para asegurar que la imagen cargue perfecto desde /assets ---
    image_side = rx.box(
        rx.image(
            src=image_url,
            width="100%",
            height="100%",
            object_fit="cover", # Evita que se deformen
        ),
        flex="1",
        min_height="580px",
        background_color="#F3F3F3", # Un fondito sutil por si tarda en cargar
        display="flex",
        align_items="center",
        justify_content="center",
        overflow="hidden",
    )

    details_side = rx.vstack(
        rx.text(f"N. {product_id}", font_size="0.62rem", letter_spacing="0.45em", color=GOLD, text_transform="uppercase"),
        rx.heading(name, font_family="'Cormorant Garamond', serif", font_size="3rem", font_weight="300", color=INK, letter_spacing="0.03em", line_height="1.05"),
        rx.text(subtitle, font_family="'Cormorant Garamond', serif", font_size="1.05rem", font_weight="300", color=TAUPE, font_style="italic", margin_top="0.5rem"),
        rx.box(height="0.5rem"),
        rx.box(background=WARM_GRAY, height="1px", width="100%", margin_y="1.5rem"),
        rx.text(price, font_size="1.6rem", font_weight="300", color=INK, letter_spacing="0.05em", font_family="'Cormorant Garamond', serif"),
        rx.box(height="1.5rem"),
        rx.text("Talla", font_size="0.62rem", letter_spacing="0.3em", color=TAUPE, text_transform="uppercase"),
        
        # Selector de tallas
        rx.hstack(
            *[
                rx.button(
                    s,
                    on_click=PageState.set_size(product_id, s),
                    background=rx.cond(PageState.selected_sizes[product_id] == s, INK, "transparent"),
                    color=rx.cond(PageState.selected_sizes[product_id] == s, CREAM, TAUPE),
                    border=rx.cond(PageState.selected_sizes[product_id] == s, f"1px solid {INK}", f"1px solid {WARM_GRAY}"),
                    border_radius="0", font_size="0.68rem", letter_spacing="0.08em",
                    padding="0.55rem 1rem", cursor="pointer", transition="all 0.2s ease",
                    _hover={"border_color": INK, "color": INK},
                )
                for s in sizes
            ],
            gap="0.5rem", flex_wrap="wrap", margin_top="0.75rem",
        ),
        rx.box(height="2rem"),
        
        # Botón de añadir a carrito
        rx.cond(
            PageState.added[product_id],
            rx.vstack(
                rx.hstack(
                    rx.box(background=GOLD, width="6px", height="6px", border_radius="50%"),
                    rx.text("Agregado al carrito", font_size="0.72rem", letter_spacing="0.15em", color=GOLD, text_transform="uppercase"),
                    gap="0.5rem", align="center", justify="center", width="100%",
                ),
                rx.button(
                    "Seguir comprando", on_click=PageState.reset_added(product_id),
                    background="transparent", color=TAUPE, border=f"1px solid {WARM_GRAY}", border_radius="0",
                    font_size="0.68rem", letter_spacing="0.15em", text_transform="uppercase",
                    padding="0.7rem 2rem", cursor="pointer", width="100%", _hover={"border_color": INK, "color": INK},
                ),
                rx.button(
                    "Ver carrito →", on_click=PageState.toggle_cart,
                    background=GOLD, color=WHITE, border_radius="0", font_size="0.68rem",
                    letter_spacing="0.15em", text_transform="uppercase", padding="0.7rem 2rem",
                    cursor="pointer", width="100%", _hover={"background": INK}, transition="all 0.3s ease",
                ),
                width="100%", gap="0.6rem", align="center",
            ),
            rx.button(
                "Agregar al Carrito", on_click=PageState.add_to_cart(product_id),
                background=INK, color=CREAM, border_radius="0", font_size="0.7rem",
                letter_spacing="0.2em", text_transform="uppercase", padding="1.1rem 2.5rem",
                cursor="pointer", _hover={"background": GOLD}, transition="all 0.3s ease", width="100%",
            ),
        ),
        rx.text("Edición limitada — Solo 10 ejemplares", font_size="0.62rem", color=TAUPE, letter_spacing="0.08em", margin_top="1rem", opacity="0.7"),
        align="start", justify="center", flex="1", padding="4.5rem", background=WHITE, min_height="580px",
    )

    children = [image_side, details_side] if not reverse else [details_side, image_side]
    return rx.flex(*children, direction="row", width="100%", max_width="1280px", margin="0 auto", box_shadow="0 2px 40px rgba(0,0,0,0.06)")


def grid_cards() -> rx.Component:
    """Sección de visualización de la colección de productos."""
    
    # ⚠️ AQUÍ ESTÁ LA MAGIA: Nombres e iniciales exactamente iguales a la carpeta
    products = [
        {"product_id": "01", "name": "Santiago", "subtitle": "T-shirt negro", "price": "RD$ 18,500", "image_url": "/Santiago.png", "reverse": False},
        {"product_id": "02", "name": "Bangkok",  "subtitle": "Chaqueta marrón",      "price": "RD$  9,800", "image_url": "/Bangkok.png",  "reverse": True},
        {"product_id": "03", "name": "Tokio",    "subtitle": "Camisa de seda blanca",        "price": "RD$ 12,200", "image_url": "/Tokyo.png",   "reverse": False},
        {"product_id": "04", "name": "Lisboa",   "subtitle": "Camisa denim",    "price": "RD$ 24,000", "image_url": "/Lisboa.png",  "reverse": True},
    ]
    
    return rx.box(
        section_divider("La Colección"),
        rx.vstack(
            *[rx.box(product_card(**p), padding_y="0.75rem", width="100%") for p in products],
            gap="3rem", width="100%", padding_x="2rem", padding_bottom="6rem", align="center",
        ),
        width="100%", id="coleccion", background=CREAM_DARK,
    )


def nosotros() -> rx.Component:
    """Sección sobre el Manifesto de la marca."""
    return rx.box(
        rx.vstack(
            rx.text("Il Manifesto", font_size="0.62rem", letter_spacing="0.5em", color=GOLD, text_transform="uppercase"),
            rx.heading("Menos piezas.", rx.el.br(), "Más significado.", font_family="'Cormorant Garamond', serif", font_weight="300", font_size=["2.2rem", "3.8rem"], color=INK, letter_spacing="0.04em", line_height="1.15", text_align="center"),
            rx.box(background=GOLD, height="1px", width="40px", margin_y="2.5rem"),
            rx.text("Ogni pezzo di To' Ricci nasce da una sola domanda: cosa resterebbe se eliminassi tutto il superfluo. Nessun logo in vista, nessuna tendenza, nessun rumore. Solo tessuto, forma e tempo.", font_family="'Cormorant Garamond', serif", font_size="1.2rem", font_weight="300", color=TAUPE, max_width="540px", text_align="center", line_height="1.9", font_style="italic"),
            rx.box(height="4rem"),
            rx.hstack(
                rx.vstack(rx.text("10", font_family="'Cormorant Garamond', serif", font_size="3.5rem", font_weight="300", color=INK), rx.text("Piezas por edición", font_size="0.62rem", letter_spacing="0.2em", color=TAUPE, text_transform="uppercase"), align="center", gap="0.5rem"),
                rx.box(width="1px", height="70px", background=WARM_GRAY),
                rx.vstack(rx.text("100%", font_family="'Cormorant Garamond', serif", font_size="3.5rem", font_weight="300", color=INK), rx.text("Hecho a mano", font_size="0.62rem", letter_spacing="0.2em", color=TAUPE, text_transform="uppercase"), align="center", gap="0.5rem"),
                rx.box(width="1px", height="70px", background=WARM_GRAY),
                rx.vstack(rx.text("0", font_family="'Cormorant Garamond', serif", font_size="3.5rem", font_weight="300", color=INK), rx.text("Logos visibles", font_size="0.62rem", letter_spacing="0.2em", color=TAUPE, text_transform="uppercase"), align="center", gap="0.5rem"),
                gap="4rem", align="center", justify="center", flex_wrap="wrap",
            ),
            align="center", padding="9rem 2rem",
        ),
        background=WHITE, width="100%", id="nosotros",
    )


def contacto() -> rx.Component:
    """Sección de contacto y redes sociales."""
    return rx.box(
        rx.vstack(
            rx.text("Contatti", font_size="0.62rem", letter_spacing="0.5em", color=GOLD, text_transform="uppercase"),
            rx.heading("Scrivici", font_family="'Cormorant Garamond', serif", font_weight="300", font_size="3rem", color=INK, letter_spacing="0.05em"),
            rx.box(background=GOLD, height="1px", width="40px", margin_y="2rem"),
            rx.link(rx.text("to'ricci@gmail.com", font_family="'Cormorant Garamond', serif", font_size="1.3rem", font_weight="300", color=TAUPE, letter_spacing="0.05em", _hover={"color": GOLD}, transition="color 0.3s ease"), href="mailto:toricci@gmail.com"),
            rx.box(height="1rem"),
            rx.hstack(
                rx.text("Instagram", font_size="0.65rem", letter_spacing="0.2em", color=TAUPE, text_transform="uppercase"),
                rx.text("|", color=WARM_GRAY, font_size="0.65rem"),
                rx.link(rx.text("@soloricci.official", font_size="0.65rem", letter_spacing="0.15em", color=GOLD, _hover={"color": INK}), href="https://instagram.com/soloricci.official", is_external=True),
                gap="1rem", align="center",
            ),
            align="center", padding="8rem 2rem",
        ),
        background=CREAM, border_top=f"1px solid {WARM_GRAY}", width="100%", id="contacto",
    )


def footer() -> rx.Component:
    """Pie de página."""
    return rx.box(
        rx.hstack(
            rx.text("To' Ricci — Milano", font_family="'Cormorant Garamond', serif", font_size="0.85rem", font_weight="300", letter_spacing="0.2em", color=TAUPE),
            rx.text("@copyright JRey", font_size="0.62rem", letter_spacing="0.15em", color=TAUPE, opacity="0.5"),
            justify="between", align="center", width="100%", padding="2rem 4rem",
        ),
        background=CREAM_DARK, border_top=f"1px solid {WARM_GRAY}", width="100%", id="footer",
    )


# --- Página Principal (INDEX) ---

@rx.page(route="/", title="To' Ricci — Colección N.001")
def index() -> rx.Component:
    return rx.box(
        cart_sidebar(),
        navbar(),
        hero(),
        grid_cards(),
        nosotros(),
        contacto(),
        footer(),
        background=CREAM,
        min_height="100vh",
        font_family="'DM Sans', sans-serif",
        color=INK,
    )


# --- Configuración e Inicialización de la App ---
app = rx.App(
    stylesheets=[
        "styles.css",
        "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300;1,400&family=DM+Sans:wght@300;400;500&display=swap",
    ]
)