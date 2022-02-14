def is_admin_request(ctx):
    return ctx.message.author.guild_permissions.administrator
