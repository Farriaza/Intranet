from .models import Estamento, Cargo, UnidadFiscalia, Perfil
from .forms import UserUpdateForm, PerfilUpdateForm

def perfil_context(request):
    if not request.user.is_authenticated:
        return {}

    perfil, _ = Perfil.objects.get_or_create(user=request.user)

    return {
        "user_form": UserUpdateForm(instance=request.user),
        "perfil_form": PerfilUpdateForm(instance=perfil),
        "ESTAMENTOS": Estamento.objects.all(),
        "CARGOS": Cargo.objects.all(),
        "UNIDADES": UnidadFiscalia.objects.all(),
    }
