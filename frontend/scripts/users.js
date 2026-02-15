async function getDMUsernames() {
  try {
    // 1️⃣ Get your own username from Discord's internal store
    console.log("starting getUsernames, trying to get chunk")
    let currentUser = null;

    const chunk = window.webpackChunkdiscord_app;
    if (!chunk) return null;

    console.log("trying to push chunk")
    chunk.push([
      [Math.random()],
      {},
      (req) => {
        for (let m of Object.values(req.c)) {
          try {
            if (m.exports?.default?.getCurrentUser) {
              currentUser = m.exports.default.getCurrentUser();
              break;
            }
          } catch {}
        }
      },
    ]);

    if (!currentUser) return null;

    const myUsername = currentUser.username;

    // 2️⃣ Extract channel ID from URL
    // Format: /channels/@me/CHANNEL_ID
    console.log("trying to get channel ID")
    const match = window.location.pathname.match(/\/channels\/@me\/(\d+)/);
    if (!match) return null;

    const channelId = match[1];

    // 3️⃣ Fetch channel data
    const res = await fetch(`https://discord.com/api/v9/channels/${channelId}`);
    const channelData = await res.json();

    if (!channelData.recipients || channelData.recipients.length === 0) {
      return null;
    }

    // In a 2-person DM, recipients only contains the OTHER user
    const otherUsername = channelData.recipients[0].username;

    return {
      myUsername,
      otherUsername,
    };

  } catch (err) {
    console.error("Failed to get DM usernames:", err);
    return null;
  }
}
