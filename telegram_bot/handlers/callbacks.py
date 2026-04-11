"""
Extra callback query handlers that don't belong to a specific command.
Handles the main menu buttons routing.
"""
import logging
from aiogram import Router, types, F
from .commands import cmd_haberler, cmd_portfoy, cmd_durum, cmd_arbitraj, cmd_fiyat, cmd_ai

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data == "noop")
async def noop_callback(call: types.CallbackQuery):
    await call.answer()

@router.callback_query(F.data.startswith("btn:"))
async def menu_btn_callback(call: types.CallbackQuery):
    action = call.data.split(":")[1]
    # We mock a message to re-use the command handlers
    mock_msg = call.message.model_copy(update={"from_user": call.from_user})
    if action == "haberler":
        await cmd_haberler(mock_msg)
    elif action == "portfoy":
        await cmd_portfoy(mock_msg)
    elif action == "durum":
        await cmd_durum(mock_msg)
    elif action == "koinler":
        from .commands import cmd_koinler
        await cmd_koinler(mock_msg)
    elif action == "balina":
        from .commands import cmd_son_balina
        await cmd_son_balina(mock_msg)
    elif action == "settings":
        from .admin import cmd_kontrol
        await cmd_kontrol(mock_msg)
    await call.answer()

@router.callback_query(F.data.startswith("admin:"))
async def menu_admin_callback(call: types.CallbackQuery):
    action = call.data.split(":")[1]
    mock_msg = call.message.model_copy(update={"from_user": call.from_user})
    from .admin import cmd_export_csv, cmd_start_radar, cmd_stop_radar
    from .commands import cmd_durum
    
    if action == "status":
        await cmd_durum(mock_msg)
    elif action == "export":
        await cmd_export_csv(mock_msg)
    elif action == "start":
        await cmd_start_radar(mock_msg)
    elif action == "stop":
        await cmd_stop_radar(mock_msg)
    await call.answer()

@router.callback_query(F.data.startswith("arb:"))
async def menu_arb_callback(call: types.CallbackQuery):
    symbol = call.data.split(":")[1]
    mock_msg = call.message.model_copy(update={"text": f"/arbitraj {symbol}", "from_user": call.from_user})
    await cmd_arbitraj(mock_msg)
    await call.answer()

@router.callback_query(F.data.startswith("price:"))
async def menu_price_callback(call: types.CallbackQuery):
    symbol = call.data.split(":")[1]
    mock_msg = call.message.model_copy(update={"text": f"/fiyat {symbol}", "from_user": call.from_user})
    await cmd_fiyat(mock_msg)
    await call.answer()

@router.callback_query(F.data.startswith("ai:"))
async def menu_ai_callback(call: types.CallbackQuery):
    symbol = call.data.split(":")[1]
    mock_msg = call.message.model_copy(update={"text": f"/ai {symbol} Yön ne olur?", "from_user": call.from_user})
    await cmd_ai(mock_msg)
    await call.answer()
